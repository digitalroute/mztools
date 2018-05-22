#!/usr/bin/python3
import boto3
import json
from termcolor import colored
from .common import get_repo_bucket, get_general_bucket
from .common import get_files, get_file_list


def run_get(args):

    print('Getting files...\n')

    # if args.package:
    #     get_files(bucket, args.package, prefix='packages')
    if args.config:
        if '-' in args.config:
            args.config = get_all_files(get_repo_bucket(), 'configs')

        get_files(get_repo_bucket(), args.config, prefix='configs')
    # if args.script:
    #     get_files(bucket, args.script, prefix='scripts')
    if args.extref:
        if '-' in args.extref:
            args.extref = get_all_files(get_repo_bucket(), 'extrefs')

        get_files(get_repo_bucket(), args.extref, prefix='extrefs')
    if args.file:
        if '-' in args.file:
            args.file = get_all_files(get_general_bucket(), 'files')

        get_files(get_general_bucket(), args.file, prefix='files')
    if args.python_module:
        if '-' in args.python_module:
            args.python_module = get_all_files(get_repo_bucket(), 'python-modules')

        get_files(get_repo_bucket(), args.python_module, prefix='python-modules')
    if args.python_requirement:
        if '-' in args.python_requirement:
            args.python_requirement = get_all_files(get_repo_bucket(), 'python-requirements')

        get_files(get_repo_bucket(), args.python_requirement,
                  prefix='python-requirements')

    print(colored('\n  To list files run "mztools list"\n',
                  attrs=['dark']))

    return


def get_all_files(bucket, type):

    files = []

    # Get files from repo bucket
    if type is not 'files':
        # Get only extrefs
        prefixList = [type]

        filesDict = get_file_list(bucket, prefixList)
    else:
        filesDict = get_file_list(bucket)

    if len(filesDict[type]) > 0:
        for f in filesDict[type]:
            files.append(f['name'])
    return files
