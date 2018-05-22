#!/usr/bin/python3
import boto3
import json
from termcolor import colored
from .common import run_lambda


def run_version():
    print('Fetching versions...\n')
    list_version()

    return


def list_version():
    '''List versions running in test & prod
    as well as what is ready to deploy'''

    filesDict = run_lambda('paas-tools-lambda_get-versions')

    print(colored('  Current version in:', attrs=['bold']))
    print('    Production:   ' + filesDict['current_prod_version'])
    print('    Test:         ' + filesDict['current_test_version'])
    print('    Dev:          ' + filesDict['current_dev_version'])
    print(colored('\n  Available:', attrs=['bold']))
    for version in filesDict['available']:
        print('    ' + version)

    print(colored('\n  To deploy a new version run "mztools deploy"\n',
                  attrs=['dark']))

    return()
