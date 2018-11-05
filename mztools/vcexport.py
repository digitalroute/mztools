from termcolor import colored
import os
import time
import getpass

from .common import get_parameter, list_s3_bucket_dirs, untar_bytes
from .k8sexec import K8sexec
from .kops import find_single_cluster, get_state_bucket

from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

def run_vcexport(args):
    env = args.environment
    destdir = args.directory
    if not checkdir(destdir):
        return False

    kops_state_bucket = get_state_bucket(env)
    kops_cluster_name = find_single_cluster(kops_state_bucket, env)
    if kops_cluster_name is None:
        return False

    print(colored('Running vcexport in K8s cluster '+kops_cluster_name, 'white'))
    kube = K8sexec(kops_state_bucket=kops_state_bucket, kops_cluster_name=kops_cluster_name)
    mzuser = 'mzadmin'
    if args.user:
        mzuser = args.user

    mzpasswd = getpass.getpass("Password for " + mzuser + ":")
    commands = [
        'tmpdir=`mktemp -d`',
        'echo $tmpdir is the EXPORT_DIR>&2',
        'mzsh '+mzuser+'/'+mzpasswd+' vcexport -d $tmpdir',
    ]

    exec_result = kube.exec_pod_command(command=commands, labels={ "app": "platform" })
    if not exec_result['success']:
        return False
    export_dir = None
    for row in exec_result['stderr']:
        if "the EXPORT_DIR" in row:
            export_dir = row.rsplit(' ')[0]
    if export_dir is None:
        print(colored("The command failed in Pod", 'red'))
        return False
    platform_pod_name = exec_result['pod_name']
    tarbytes = kube.tar_pod_directory(platform_pod_name, export_dir)
    kube.delete_pod_directory(platform_pod_name, export_dir)
    if not untar_bytes(tarbytes, destdir):
        print(colored("There were some errors unpacking files locally", 'red'))
    print(colored('Files have been written to directory "' + destdir + "'", 'green'))
    return True

def checkdir(destdir):
    if not os.path.isdir(destdir):
        if os.path.exists(destdir):
            print (colored('Destination directory `'+destdir+'` is not a directory',
                'red', attrs=['bold']))
            return False
        else:
            print (colored('Destination directory `'+destdir+'` does not exist',
                'red', attrs=['bold']))
            return False
    return True
