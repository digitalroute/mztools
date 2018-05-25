#!/usr/bin/python3
import boto3
import botocore
from termcolor import colored


def run_info(args):
    print(colored('Customer: ',
          'white', attrs=['bold']) + get_parameter('/customer/name'))
    print('')

    print(colored('Platform versions: ',
          'white', attrs=['bold']))

    print('')

    print('Dev:  ' + get_parameter('/dev/platform/version'))
    print('Test: ' + get_parameter('/test/platform/version'))
    print('Prod: ' + get_parameter('/prod/platform/version'))

    print('')

    print(colored('EC versions: ',
          'white', attrs=['bold']))

    print('')

    print('Dev:  ' + get_parameter('/dev/ec/version'))
    print('Test: ' + get_parameter('/test/ec/version'))
    print('Prod: ' + get_parameter('/prod/ec/version'))

    return


def get_parameter(param):
    try:
        ssmClient = boto3.client('ssm')
        response = ssmClient.get_parameter(
            Name=param,
            WithDecryption=False
        )['Parameter']['Value']
        return response
    except botocore.exceptions.ClientError:
        return '-'
