#!/usr/bin/python3
import boto3
import json
import sys
from time import sleep
from termcolor import colored
from .common import run_lambda, SpinCursor, poll_build, get_parameter

def get_pod_name(env, container):

    pod_name = ''
    response = run_lambda('paas-tools-lambda_get-status', {
        'environment': env
    })

    try:
        for pod in response['status']:
            instance_name = pod.get('instance_name','Not available')

            if instance_name.startswith(container+'-'):
                pod_name = instance_name

    except KeyError as e:
        print('  Unable to get ' + container + ' status.')

    return pod_name

def restart_pod(env, name):

    res = run_lambda('paas-tools-lambda_restart-pico', {
        'environment': env,
        'name': name
    })
    print('  Restarting wd instance' + res + '\n')
    return

def run_deploy(args):

    if args.test:
        if check_version(args.test[0], 'test'):
            print('You are trying to deploy the same version again.')
            print('Please pick another version to deploy.')
            return False

        print('Triggering deploy...\n')
        deploy_container('test', args.test[0])
    if args.promote:
        if check_version(get_parameter('/test/platform/version'), 'prod'):
            print('You are trying to deploy the same version again.')
            print('Deploy a another version to test for the ability to promote.')
            return False

        question = '\nAre you sure you want to promote test to production? '
        question += '[yes/no]: '
        verification = input(question)
        while verification != 'yes':
            if verification == 'no':
                sys.exit(0)
            print('Please answer "yes" or "no"')
            verification = input(question)

        print('Promoting test to production...\n')
        deploy_container('prod')
    if args.dev:
        if check_version(args.dev[0], 'dev'):
            print('You are trying to deploy the same version again.')
            print('Please pick another version to deploy.')
            return False

        if args.reset:
            reset = True
            print(colored(
                '\nThis will wipe all data in dev and deploy version: {}.'
                .format(args.dev[0]),
                attrs=['bold']
                )
            )
            question = '\nAre you sure you want to reset the dev env? '
            question += '[yes/no]: '
            verification = input(question)
            while verification != 'yes':
                if verification == 'no':
                    sys.exit(0)
                print('Please answer "yes" or "no"')
                verification = input(question)

            print('Resetting dev with version {}...\n'.format(args.dev[0]))
        else:
            reset = False

        deploy_container('dev', args.dev[0], reset)

    return True


def check_version(version, env):
    # Check that the version we are trying to deploy is not the same as
    # the one that is already deployed
    if version == get_parameter('/' + env + '/platform/version'):
        print('Trying to deploy: ' + version)
        print('Version in ' + env + ': ' + version)
        return True
    return False

def deploy_container(environment=None, version=None, reset=False):

    if environment == 'prod':
        msg = 'Promoting test to prod...'
    else:
        msg = 'Deploying ' + version + ' to ' + environment + '...'

    print(colored('\n  ' + msg, attrs=['bold']))

    response = run_lambda('paas-tools-lambda_post-deploy', {
        'version': version,
        'env': environment,
        'reset': reset
    })

    try:
        print('    Platform'.ljust(20), end='')
        if response['platform']['Status'] == "Failed":
            print(colored('Failed!', 'red', attrs=['bold']))
        elif response['platform']['Status'] == "Success":
            print(colored('OK', 'green', attrs=['bold']))
    except KeyError:
        print(colored('Unknown', 'yellow', attrs=['bold']))

    try:
        print('    EC'.ljust(20), end='')
        if response['ec']['Status'] == "Failed":
            print(colored('Failed!', 'red', attrs=['bold']))
        elif response['ec']['Status'] == "Success":
            print(colored('OK', 'green', attrs=['bold']))
    except KeyError:
        print(colored('Unknown', 'yellow', attrs=['bold']))

    print('')

    pod_name = get_pod_name(environment, 'wd')
    if pod_name:
        restart_pod(environment, pod_name)
    else:
        print('  Please restart web desktop in the ' + environment + ' environment.\n')

    if environment == 'test':
        print(colored('  To promote test to prod run "mztools deploy -p"\n',
                      attrs=['dark']))

    return
