#!/usr/bin/python3
import boto3
import json
from termcolor import colored
from .common import run_lambda


def run_version():
    print('Fetching versions...\n')
    list_version()

    return True


def list_version():
    '''List versions running in test & prod
    as well as what is ready to deploy'''

    filesDict = run_lambda('paas-tools-lambda_get-versions')

    print(colored('  Current version in:', attrs=['bold']))
    print('    Prod:         ' + filesDict['current_prod_version'])
    print('    Test:         ' + filesDict['current_test_version'])
    print('    Dev:          ' + filesDict['current_dev_version'])
    print(colored('\n  Available:', attrs=['bold']))

    i = 0
    max = 10
    tot_ver = len(filesDict['available'])

    # limited to 20 versions. Print out in 10 rows 2 columns format
    while i < max:
        ver_c1 = filesDict['available'][i]
        ver_c2 = ''

        if i + max < tot_ver: # version more than 10 will print at second column
            ver_c2 = filesDict['available'][i + 10]

        print('    ' + ver_c1.ljust(50) + ver_c2)
        i = i + 1

    print(colored('\n  To deploy a new version run "mztools deploy"\n',
                  attrs=['dark']))

    return()
