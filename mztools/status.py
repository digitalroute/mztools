#!/usr/bin/python3
import boto3
import json
from ast import literal_eval
from termcolor import colored
from .common import run_lambda

# Containers to display
containers = (
    'platform-',
    'ec-',
    'wd-'
)


def status_color(status):
    if status == 'running':
        return('green')
    elif status == 'waiting':
        return('yellow')
    else:
        return('red')


def run_status(args):

    if args.environment:
        print('Fetching status...\n')
        get_status(args)

    return


def get_status(args):
    env = args.environment
    verbose = args.verbose
    if verbose:
        columnWidth = 27
    else:
        columnWidth = 24

    result = []

    response = run_lambda('paas-tools-lambda_get-status', {
        'environment': env
    })

    header = 'Instance Name'.ljust(columnWidth)
    header += 'Image'.ljust(columnWidth)
    header += 'Status'
    if verbose:
        header += ' (UTC)'
    header += '\n'

    print(colored(header, attrs=['bold']))

    try:
        for pod in response['status']:
            if pod['instance_name'].startswith(containers):

                # Instance name
                if verbose:
                    line = pod['instance_name'].ljust(columnWidth)
                else:
                    line = pod['instance_name'].split('-')[0]\
                        .ljust(columnWidth)

                # Image name and version
                line += pod['image'].split('/')[-1].ljust(columnWidth)

                # Status and timestamp
                line += colored(
                    pod['status'].capitalize().ljust(11),
                    status_color(pod['status']))
                if verbose:
                    line += pod['timeStamp']
                print(line)

    except KeyError as e:
        print('Unable to get status, please try again')

    print()
    return
