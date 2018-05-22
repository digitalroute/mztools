#!/usr/bin/python3
import boto3
import json
from termcolor import colored
from .common import get_repo_bucket, get_general_bucket, get_file_list


def run_list(args):
    print('Fetching files...\n')

    argsList = []

    if args:
        #if args.package:
        #    argsList.append('package')
        if args.config:
            argsList.append('configs')
        #if args.script:
        #    argsList.append('scripts')
        if args.extref:
            argsList.append('extrefs')
        if args.file:
            argsList.append('files')
        if args.python_module:
            argsList.append('python-modules')
        if args.python_requirement:
            argsList.append('python-requirements')
    else:
        argsList.append('configs')
        argsList.append('extrefs')
        argsList.append('files')
        argsList.append('python-modules')
        argsList.append('python-requirements')
        #argsList.append('scripts')
        #argsList.append('package')

    list_files(argsList)

    return


def list_files(argsList):
    '''List files currently in bucket'''

    # Get repo bucket files
    prefixList = [
        'packages',
        'configs',
        'scripts',
        'extrefs',
        'python-modules',
        'python-requirements'
    ]

    # Get files from repo bucket
    filesDict = get_file_list(get_repo_bucket(), prefixList)

    # Get files from general bucket
    if 'files' in argsList:
        generalFilesDict = get_file_list(get_general_bucket())

    # Get all items in a list to find longest word to set column width
    allItems = ['defaultvalueofsomelength']
    for key, val in filesDict.items():
        for fileDict in val:
            for subKey, subVal in fileDict.items():
                allItems.append(subVal)
    name_col_width = max(len(word) for word in allItems) + 2
    size_col_width = 15
    modified_col_width = 20

    # Print header
    header = 'Name:'.ljust(name_col_width)
    header += '  Size:'.ljust(size_col_width)
    header += '  Last modified:'.ljust(modified_col_width)
    print('  ' + colored(header, attrs=['bold']))

    # Print files
    for fileType in argsList:
        if fileType is 'files':
            files = generalFilesDict
        else:
            files = filesDict

        if len(files[fileType]) > 0:
            print(colored('\n  ' + fileType.capitalize() + ':',
                  attrs=['bold']))
            for f in files[fileType]:
                line = '    ' + f['name'].ljust(name_col_width)
                line += f['size'].ljust(size_col_width)
                line += f['modified'].ljust(modified_col_width)
                print(line)

    print(colored('\n  To build a new container run "mztools build"\n',
                  attrs=['dark']))

    return()
