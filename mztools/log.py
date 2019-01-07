#!/usr/bin/python3
import boto3
import json
from termcolor import colored
from .common import run_lambda, get_log_stream


def run_log(args):

    if args.environment:
        print('Fetching log...\n')
        get_log(args)

    return True


def get_log(args):
    env = args.environment

    logEvents = get_log_stream('/' + env + '/platform')

    for line in logEvents:
        splitLine = line.split(' - ', 1)
        print(splitLine[0] + ' : ' + splitLine[1])
