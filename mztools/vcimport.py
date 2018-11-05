from termcolor import colored
import os
import time
import getpass

from .common import get_parameter, list_s3_bucket_dirs, tar_directory
from .k8sexec import K8sexec
from .kops import find_single_cluster, get_state_bucket

from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

def run_vcimport(args):
    env = args.environment
    mzuser = 'mzadmin'
    srcdir = args.directory
    if not checkdir(srcdir):
        return False

    tarbytes = tar_directory(srcdir)
    if tarbytes is None:
        print(colored("There were some errors packing files locally", 'red'))

    kops_state_bucket = get_state_bucket(env)
    kops_cluster_name = find_single_cluster(kops_state_bucket, env)
    if kops_cluster_name is None:
        return False

    print(colored('Running vcimport in K8s cluster '+kops_cluster_name, 'white'))
    kube = K8sexec(kops_state_bucket=kops_state_bucket, kops_cluster_name=kops_cluster_name)

    commands = [
        'tmpdir=`mktemp -d`',
        'echo $tmpdir is the IMPORT_DIR>&2',
    ]
    exec_result = kube.exec_pod_command(command=commands, labels={ "app": "platform" })
    if not exec_result['success']:
        return False
    import_dir = None
    for row in exec_result['stderr']:
        if "the IMPORT_DIR" in row:
            import_dir = row.rsplit(' ')[0]
    if import_dir is None:
        print(colored("The command failed in Pod", 'red'))
        return False

    platform_pod_name = exec_result['pod_name']
    kube.untar_pod_directory(tarbytes, pod_name=platform_pod_name, dest_dir=import_dir)
    if not exec_result['success']:
        print(colored('tar failed in pod:', 'red'))
        print(exec_result['stderr'])
        return False

    if args.user:
        mzuser = args.user
    mzpasswd = getpass.getpass("Password for " + mzuser + ":")

    commands = [
        # Fixme remove echo after verifying that this command is safe
        'echo mzsh '+mzuser+'/'+mzpasswd+' vcimport -d $tmpdir'
    ]
    exec_result = kube.exec_pod_command(command=commands, pod_name = platform_pod_name)
    if not exec_result['success']:
        return False
    kube.delete_pod_directory(platform_pod_name, import_dir)

    print(colored('Files have been imported from directory "' + import_dir + "'", 'green'))
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
