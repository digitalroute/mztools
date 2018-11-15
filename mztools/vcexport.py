from termcolor import colored
import os, sys, glob
import time
import getpass
from base64 import standard_b64decode

from .common import untar_bytes, run_lambda, allow_one

def run_vcexport(args):
    env = allow_one(args.environment)
    destdir = args.directory
    overwrite = args.overwrite
    if not checkdir(destdir, overwrite):
        return False

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
    if args.excludesysdata:
        mzsh_extraargs+= " -es"
    if args.includemeta:
        mzsh_extraargs+= " -im"
    if args.folders:
        mzsh_extraargs+= " -f " + ' '.join(args.folders)

    response = run_lambda('paas-tools-lambda_mzsh-vcexport', {
        'env': env,
        'mzuserpasswd': mzuser+'/'+mzpasswd,
        'mzsh_extraargs': mzsh_extraargs
    })

    if 'tarfile' not in response or response['tarfile'] is None:
        print(colored('The remote function failed:','red'))
        return False
    tarbytes = response['tarfile']
    if len(response['stdout']) > 0:
        print(colored(response['stdout'],'blue'))
    if len(response['stderr']) > 0:
        print(colored(response['stderr'],'red'))
    if not untar_bytes(standard_b64decode(tarbytes), destdir):
        print(colored("There were some errors unpacking files locally", 'red'))
        return False
    if checkexportok(destdir, args.folders):
        print(colored('Files have been written to directory "' + destdir + "'", 'green'))
        return True
    else:
        return False

def checkdir(destdir, overwrite):
    if not os.path.isdir(destdir):
        if os.path.exists(destdir):
            print (colored('Destination directory `'+destdir+'` is not a directory',
                'red', attrs=['bold']))
            return False
        else:
            try:
                os.mkdir(destdir, 0o755)
            except Exception as e:
                sys.stderr.write(e)
                return False
            return True
    if not overwrite:
        for filename in os.listdir(destdir):
            if filename[0] != '.':
                print (colored('Destination directory `'+destdir+'` is not empty and overwrite (dangerous!) was not specified',
                    'red', attrs=['bold']))
                return False
    return True

def listdir_nohidden(dirtolist):
    return list(map(lambda x: os.path.basename(x),glob.glob(os.path.join(dirtolist, '*'))))

def checkexportok(destdir, folders):
    created_dirs = listdir_nohidden(destdir)
    if len(created_dirs) < 1:
        print(colored('Export did not yield any folders', 'red'))
        return False
    if folders:
        for f in folders:
            if f not in created_dirs:
                sys.stderr.write('Warning: folder "' + f + '" was not found in the export\n')
    return True
