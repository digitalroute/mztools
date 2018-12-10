from termcolor import colored
import os
import time
import getpass

from .common import tar_directory, run_lambda, allow_one, s3_put_bytes, get_parameter

def run_vcimport(args):
    env = allow_one(args.environment)
    srcdir = args.directory
    if not checkdir(srcdir):
        return False

    tarbytes = tar_directory(srcdir)
    if tarbytes is None:
        print(colored("There were some errors packing files locally", 'red'))

    mzuser = 'mzadmin'
    mzpasswd = None
    if args.user:
        if '/' in args.user:
            mzpasswd = args.user.split('/',2)[1]
            mzuser = args.user.split('/',2)[0]
        else:
            mzuser = args.user
    if mzpasswd is None:
        mzpasswd = getpass.getpass("Password for " + mzuser + ":")
    mzsh_extraargs = ""
    if args.message:
        mzsh_extraargs+= ' -m "'+args.message.replace('"','”')+'"'
    if args.dryrun:
        mzsh_extraargs+= " -y"
    if args.folders:
        mzsh_extraargs+= " -f " + ' '.join(args.folders)

    transfer_bucket = get_parameter('/'+env+'/mztools-transfer-bucket')
    s3path = s3_put_bytes(tarbytes, transfer_bucket)
    response = run_lambda('paas-tools-lambda_mzsh-vcimport', {
        'tarfile': s3path,
        'env': env,
        'mzuserpasswd': mzuser+'/'+mzpasswd,
        'mzsh_extraargs': mzsh_extraargs
    })
    if 'mzsh_stderr' in response and len(response['mzsh_stderr']) > 0:
        print(colored(response['mzsh_stderr'], 'red'))
    if not 'mzsh_stdout' in response or len(response['mzsh_stdout']) < 3:
        print(colored("Import failed to execute mzsh", 'red'))
        if 'errorMessage' in response:
            print(colored('Lambda error: '+ response['errorMessage'],'red'))
        return False
    print(colored(response['mzsh_stdout'].rstrip(), 'blue'))
    return True

def checkdir(srcdir):
    if not os.path.isdir(srcdir):
        if os.path.exists(srcdir):
            print (colored('Source directory `'+srcdir+'` is not a directory',
                'red', attrs=['bold']))
            return False
        else:
            print (colored('Source directory `'+srcdir+'` does not exist',
                'red', attrs=['bold']))
            return False
    return True
