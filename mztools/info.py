#!/usr/bin/python3

from termcolor import colored
from .common import get_parameter


def run_info(args):
    print(colored('Company: ',
          'white', attrs=['bold']) + get_parameter('/customer/name'))
    print('')

    print(colored('Deployed versions: ',
          'white', attrs=['bold']))

    print('')

    print('Dev:  ' + get_parameter('/dev/platform/version'))
    print('Test: ' + get_parameter('/test/platform/version'))
    print('Prod: ' + get_parameter('/prod/platform/version'))

    print('')

    return True
