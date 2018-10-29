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

    return True


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
    header += 'Status'.ljust(11)
    if verbose:
        header += '(UTC)'
    header += '\n'

    print(colored(header, attrs=['bold']))

    try:
        for pod in response['status']:
            instance_name = pod.get('instance_name','Not available')
            if instance_name.startswith(containers):

                # Instance name
                if verbose:
                    line = instance_name.ljust(columnWidth)
                else:
                    line = instance_name.split('-')[0]\
                        .ljust(columnWidth)

                # Image name and version
                image = pod.get('image','Not available')
                line += image.split('/')[-1].ljust(columnWidth)

                # Status and timestamp
                status = pod.get('status','Unknown')
                timestamp = pod.get('timeStamp','Not available')
                line += colored(
                    status.capitalize().ljust(11),
                    status_color(status))
                if verbose:
                    line += timestamp
                print(line)

    except KeyError as e:
        print('Unable to get status, please try again')

    print()
    return
