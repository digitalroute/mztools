#!/usr/bin/python3
import boto3
import json
from termcolor import colored
from .common import get_repo_bucket, get_general_bucket, put_files, put_folder


def run_put(args):
    print('Putting files...\n')

    # if args.package:
    #     put_files(bucket, args.package, prefix='packages')
    if args.config:
        put_files(get_repo_bucket(), args.config, prefix='configs')
    # if args.script:
    #     put_files(bucket, args.script, prefix='scripts')
    if args.extref:
        put_files(get_repo_bucket(), args.extref, prefix='extrefs')
        print(colored('\nExtrefs are located in /extrefs after you build your image.', attrs=['dark']))
    if args.file:
        put_files(get_general_bucket(), args.file, prefix='files')
    if args.python_module:
        put_folder(get_repo_bucket(), args.python_module, prefix='python-modules')
    if args.python_requirement:
        put_files(get_repo_bucket(), args.python_requirement,
                  prefix='python-requirements')

    print(colored('\nTo list files run "mztools list"\n',
                  attrs=['dark']))

    return
