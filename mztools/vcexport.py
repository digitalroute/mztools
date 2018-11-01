from termcolor import colored
from .common import get_parameter
from subprocess import run, DEVNULL, Popen, PIPE
import boto3
import os
import time
import getpass
from base64 import standard_b64decode

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

def run_vcexport(args):
    env = args.environment
    destdir = args.directory
    kops_state_bucket=get_parameter('/'+env+'/kubernetes/state-bucket')
    matching_clusters = find_kops_cluster_names(kops_state_bucket, env)
    if len(matching_clusters) > 1:
        print (colored('There are multiple matching cluster names in the state bucket - aborting',
            'red', attrs=['bold']))
        return False
    if len(matching_clusters) < 1:
        print (colored('There are no matching cluster names in the state bucket - aborting',
            'red', attrs=['bold']))
        return False
    print(colored('Running vcexport in K8s cluster '+matching_clusters[0], 'white'))

    # FIXME: make kubeconfigtmp a safe temp file and delete it after running the vcexport
    if not export_kops_kubecfg(kops_state_bucket, matching_clusters[0], '.kubeconfigtmp'):
        return False

    config.load_kube_config(config_file='.kubeconfigtmp')
    c = Configuration()
    c.assert_hostname = False
    Configuration.set_default(c)
    api = core_v1_api.CoreV1Api()

    platform_pod_name = find_pod_by_label(api, 'app', 'platform')
    print(colored('Running mzsh export in pod ' + platform_pod_name, 'white'))
    mzuser = 'mzadmin'
    if args.user:
        mzuser = args.user
    mzpasswd = getpass.getpass("Password for " + mzuser + ":")
    commands = [
        'tmpdir=`mktemp -d`',
        'echo $tmpdir is the EXPORT_DIR>&2',
        'mzsh '+mzuser+'/'+mzpasswd+' vcexport -d $tmpdir',
    ]

    exec_result = exec_pod_command(api, platform_pod_name, commands)
    if not exec_result['success']:
        return False
    export_dir = None
    for row in exec_result['stderr']:
        if "the EXPORT_DIR" in row:
            export_dir = row.rsplit(' ')[0]
    if export_dir is None:
        return False
    base64_file = copy_pod_directory(api, platform_pod_name, export_dir)
    delete_pod_directory(api,platform_pod_name, export_dir)
    tarpipe = Popen(["tar", "-C", destdir, "-xf", "-"], stdin=PIPE)
    tarpipe.stdin.write(standard_b64decode(base64_file))
    tarpipe.stdin.close()
    if tarpipe.wait() != 0:
        print(colored("There were some errors unpacking files locally", 'red'))

    print(colored('Files have been written to directory "' + destdir + "'", 'green'))
    return True

def find_kops_cluster_names(s3_bucketname, env):
    cluster_name=get_parameter('/'+env+'/kubernetes/cluster-name')
    bucket=boto3.resource('s3').Bucket(s3_bucketname)
    cluster_candidates = list(set(map(lambda o: o.key.rsplit('/')[0], bucket.objects.all())))
    matching_clusters = list()
    for candidate in cluster_candidates:
        if cluster_name+'.'+env in candidate:
            matching_clusters.append(candidate)
    return matching_clusters

def export_kops_kubecfg(state_bucket, cluster_name, kubecfg_file):
    kops_env=os.environ.copy()
    kops_env['KUBECONFIG']= kubecfg_file
    try:
        kops = run(["kops", '--state=s3://'+state_bucket, "export", "kubecfg", cluster_name],
            stdout=DEVNULL,
            env=kops_env)
    except FileNotFoundError:
        print (colored('Could not execute `kops`, please install it according to https://github.com/kubernetes/kops', 'red', attrs=['bold']))
        return False
    return True

def find_pod_by_label(api, label, value):
    resp = None
    try:
        resp = api.list_namespaced_pod(namespace='default')
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)
    #{'items': [{'metadata': {'labels': {'app': 'platform',
    for pod in resp.items:
        if 'app' in pod.metadata.labels:
            if "platform" == pod.metadata.labels['app']:
                return pod.metadata.name

    return None

def exec_pod_command(api, pod_name, commands):
    # Calling exec interactively.
    exec_command = ['/bin/sh']
    resp = stream(api.connect_get_namespaced_pod_exec, pod_name, 'default',
                  command=exec_command,
                  stderr=True, stdin=True,
                  stdout=True, tty=False,
                  _preload_content=False)
    result = { "stderr": [], "stdout": [], "success": False}
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            result['stdout'].append(resp.read_stdout())
        if resp.peek_stderr():
            result['stderr'].append(resp.read_stderr())
        if commands:
            c = commands.pop(0)
            resp.write_stdin(c + "\n")
            result['success'] = True
        else:
            break

    resp.write_stdin("echo ALL done\n")

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            buf=resp.read_stdout(timeout=3)
            if buf is not None:
                if 'ALL done' in buf:
                    result['stdout'].append(buf[:-9])
                    break
                result['stdout'].append(buf)
        if resp.peek_stderr():
            result['stderr'].append(resp.read_stderr())
    resp.close()
    return result

def copy_pod_directory(api, pod_name, dir):
    exec_command = ['/bin/sh']
    resp = stream(api.connect_get_namespaced_pod_exec, pod_name, 'default',
                  command=exec_command,
                  stderr=True, stdin=True,
                  stdout=True, tty=False,
                  _preload_content=False)

    resp.write_stdin("tar -C "+dir+" -cf - . | base64\n")
    resp.write_stdin("echo ALL done\n")

    result = { "stderr": [], "stdout": [], "success": False}
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            buf=resp.read_stdout(timeout=3)
            if buf is not None:
                if 'ALL done' in buf:
                    result['stdout'].append(buf[:-9])
                    break
                result['stdout'].append(buf)
        if resp.peek_stderr():
            result['stderr'].append(resp.read_stderr())
    resp.close()
    return "-".join(result['stdout'])

def delete_pod_directory(api, pod_name, dir):
    exec_pod_command(api, pod_name, ["rm -r " + dir])
