#!/usr/bin/python3

from termcolor import colored
from .common import get_parameter


def run_info(args):
    print(colored('Company: ',
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
