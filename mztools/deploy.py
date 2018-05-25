#!/usr/bin/python3
import boto3
import json
import sys
from time import sleep
from termcolor import colored
from .common import run_lambda, SpinCursor, poll_build


def run_deploy(args):
    if args.no_ec:
        ec = False
    else:
        ec = True

    if args.test:
        print('Triggering deploy...\n')
        deploy_container(ec, 'test', args.test[0])
    if args.promote:
        question = '\nAre you sure you want to promote test to production? '
        question += '[yes/no]: '
        verification = input(question)
        while verification != 'yes':
            if verification == 'no':
                sys.exit(0)
            print('Please answer "yes" or "no"')
            verification = input(question)

        print('Promoting test to production...\n')
        deploy_container(ec, 'prod')
    if args.dev:
        print(colored(
            '\nThis will wipe all data in dev and deploy version: {}.'.format(
                args.dev[0]
            ),
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
        deploy_container(ec, 'dev', args.dev[0])

    return


def deploy_container(ec, environment=None, version=None):
    response = run_lambda('paas-tools-lambda_post-deploy', {
        'version': version,
        'env': environment,
        'ec': ec
    })

    if environment == 'prod':
        msg = 'Promoting test to prod...'
    else:
        msg = 'Deploying ' + version + ' to ' + environment + '...'

    print(colored('  ' + msg, attrs=['bold']), end='')

    try:
        if response['platform']['Status'] == "Failed":
            print(colored('Failed!',
                  'red', attrs=['bold']))
            print('  - Does the Platform version exist?\n')
            return
    except KeyError:
        print(colored('OK', 'green', attrs=['bold']))

    try:
        if response['ec']['Status'] == "Failed":
            print('\n' + colored('  EC failed to deploy.',
                  'red', attrs=['bold']))
            print('\n  Does the EC version exist?')
            return
    except KeyError:
        print(colored('OK', 'green', attrs=['bold']))

    if environment == 'test':
        print(colored('\n  To promote test to prod run "mztools deploy -p"\n',
                      attrs=['dark']))

    return
