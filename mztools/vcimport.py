from termcolor import colored
import os, sys
import time
import getpass

from .common import tar_directory, run_lambda, allow_one, s3_put_bytes, get_parameter, get_log_stream_events

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
    # Lambda functions can be run multiple times for the same invokation
    # If the response we have is from an invokation that was redundant,
    # we must fetch the result from a cloudwatch log
    if 'mzsh_stdout' in response and response['mzsh_stdout'].rstrip() == "see cloudwatch log for details":
        print(colored("Waiting 30s for import log to appear", 'green'))
        time.sleep(30)
        mzsh_out = get_mzsh_import_log()
    else:
        mzsh_out = response
    if 'mzsh_stderr' in mzsh_out and len(mzsh_out['mzsh_stderr']) > 0:
        print(colored(mzsh_out['mzsh_stderr'], 'red'))
    if not 'mzsh_stdout' in mzsh_out or len(mzsh_out['mzsh_stdout']) < 3:
        print(colored("Import failed to execute mzsh", 'red'))
        if 'errorMessage' in response:
            print(colored('Lambda error: '+ response['errorMessage'],'red'))
        return False
    print(colored(mzsh_out['mzsh_stdout'].rstrip(), 'blue'))
    return True

def get_mzsh_import_log():
    logEvents = get_log_stream_events('/aws/lambda/paas-tools-lambda_mzsh-vcimport', timeWindow=120)

    out = { "mzsh_stderr": "", "mzsh_stdout": "" }
    for line in logEvents:
        splitStdout = line.split('mzsh_stdout>>', 1)
        if len(splitStdout) > 1:
            out["mzsh_stdout"] += splitStdout[1] + "\n"
        splitStderr = line.split('mzsh_stderr>>', 1)
        if len(splitStderr) > 1:
            out["mzsh_stderr"] += splitStderr[1] + "\n"
    return out

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
