#!/usr/bin/python3
import boto3
import json
import sys
from termcolor import colored
from .common import run_lambda, get_repo_bucket, get_general_bucket, delete_files


def run_delete(args):
    print('Checking files...\n')

    filesToDelete = {}
    repoBucket = get_repo_bucket()
    generalBucket = get_general_bucket()

    if args.config:
        filesToDelete['configs'] = {
            'bucket': repoBucket,
            'files': args.config,
            'prefix': 'repo/configs'
        }
    if args.extref:
        filesToDelete['extrefs'] = {
            'bucket': repoBucket,
            'files': args.extref,
            'prefix': 'repo/extrefs'
        }
    if args.file:
        filesToDelete['files'] = {
            'bucket': generalBucket,
            'files': args.file,
            'prefix': ''
        }
    if args.python_module:
        filesToDelete['python-modules'] = {
            'bucket': repoBucket,
            'files': args.python_module,
            'prefix': 'repo/python-modules'
        }
    if args.python_requirement:
        filesToDelete['python-requirements'] = {
            'bucket': repoBucket,
            'files': args.python_requirement,
            'prefix': 'repo/python-requirements'
        }

    delete_files(filesToDelete)

    print(colored('\nTo list files run "mztools list"\n',
                  attrs=['dark']))

    return
