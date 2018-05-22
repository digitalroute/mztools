#!/usr/bin/python3
import boto3
import json
from termcolor import colored
from .common import run_lambda, get_log_stream


def run_log(args):

    if args.environment:
        print('Fetching log...\n')
        get_log(args)

    return


def get_log(args):
    env = args.environment
    if args.json:
        pretty = False
    else:
        pretty = True

    logGroup = '/' + env + '/cluster'

    logEvents = get_log_stream(
        logGroup,
        prefix='kubernetes.var.log.containers.platform'
        )

    fileName = env + '-platform.log'
    with open(fileName, 'w') as logFile:
        for line in logEvents:
            splitLine = line.split(' - ', 1)
            if pretty:
                dictLine = json.loads(splitLine[1])
                print(splitLine[0] + ' : ' + dictLine['log'].rstrip())
            else:
                logFile.write(splitLine[1] + '\n')

        if not pretty:
            print(colored('  Please see log: "' + fileName + '"\n', 'green'))
