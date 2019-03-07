#!/usr/bin/python3
from .common import run_lambda
import re

# Allowed containers
containers = (
    '^platform$',
    '^ec[0-9]*$',
    '^wd$'
)

def run_restart(args):

    if args.environment:

        env = args.environment
        name = args.name

        # validate name
        valid = False
        for n in containers:
            if re.search(n, name, re.IGNORECASE):
                valid = True

        if not valid:
            print('Enter a valid pico name for restart')
            return False

        # get the list of pods
        response = run_lambda('paas-tools-lambda_get-status', {
            'environment': env
        })

        # find matching pod
        print('Initiating restart trigger...\n')
        pod_found = False
        for pod in response['status']:
            instance_name = pod.get('instance_name','Not available')
            container_name = instance_name.split('-')[0]
            if container_name.lower() == name.lower():
                pod_found = True
                res = run_lambda('paas-tools-lambda_restart-pico', {
                    'environment': env,
                    'name': instance_name
                })
                print(res)
                print('\nUse the status command to get info about the state of the picos.\n')
                return True

        print("Failed to find specified pico: {0}".format(name))
        return False

    return True
