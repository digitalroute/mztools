#!/usr/bin/python3
from termcolor import colored
from .common import get_file_list


def run_list(args):
    print('Fetching files...\n')

    argsList = []

    if args:
        if args.config:
            argsList.append('configs')
        if args.extref:
            argsList.append('extrefs')
        if args.file:
            argsList.append('files')
        if args.python_module:
            argsList.append('python-modules')
        if args.python_requirement:
            argsList.append('python-requirements')
        if args.backup:
            argsList.append('backups')
    else:
        argsList.extend([
            'configs',
            'extrefs',
            'files',
            'python-modules',
            'python-requirements',
            'backups'
        ])

    list_files(argsList)

    return


def list_files(argsList):
    '''List files currently in bucket'''

    # Get files
    files = get_file_list(argsList)

    name_col_width = 40
    size_col_width = 15
    modified_col_width = 20

    # Print header
    header = 'Name:'.ljust(name_col_width)
    header += '  Size:'.ljust(size_col_width)
    header += '  Last modified:'.ljust(modified_col_width)
    print('  ' + colored(header, attrs=['bold']))

    # Print files
    for fileType in argsList:
        if len(files[fileType]) > 0:
            print(colored('\n  ' + fileType.capitalize() + ':',
                  attrs=['bold']))
            for f in files[fileType]:
                name = f['name']

                if name:
                    lineName = '    ' + name.ljust(name_col_width)
                    lineSize = f['size'].ljust(size_col_width)
                    lineModified = f['modified'].ljust(modified_col_width)

                    # If filename is too long, add a new line
                    if len(name) > 40:
                        print(lineName)
                        print(
                            ''.ljust(name_col_width + 4)
                            + lineSize + lineModified)
                    else:
                        print(lineName + lineSize + lineModified)

    print(colored('\n  To build a new container run "mztools build"\n',
                  attrs=['dark']))

    return()
