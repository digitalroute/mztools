#!/usr/bin/python3
from .common import run_lambda

def run_restart(args):

    if args.environment:
        print('Initiating restart trigger...\n')

        env = args.environment
        name = args.name

        res = run_lambda('paas-tools-lambda_restart-pico', {
            'environment': env,
            'name': name
        })

    print(res)
    print('\nUse the status command to get info about the state of the picos.\n')
    return
