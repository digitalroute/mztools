#!/usr/bin/python3
import boto3
from termcolor import colored
from .common import get_extrefs_bucket, get_file_list, put_files, get_files, delete_files


def run_dev(args):

    if args.list:
        print('Listing files...\n')
        repoBucket = get_extrefs_bucket()
        run_list(repoBucket)

    if args.put_extref:
        print('Putting files...\n')
        repoBucket = get_extrefs_bucket()
        run_put(args.put_extref, repoBucket)

    if args.get_extref:
        print('Getting files...\n')
        repoBucket = get_extrefs_bucket()
        run_get(args.get_extref, repoBucket)

    if args.delete_extref:
        print('Deleting files...\n')
        repoBucket = get_extrefs_bucket()
        run_delete(args.delete_extref, repoBucket)


def run_list(bucket):

    filesDict = get_file_list(bucket, [])

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

    if len(filesDict['files']) > 0:
        for f in filesDict['files']:
            line = '    ' + f['name'].ljust(name_col_width)
            line += f['size'].ljust(size_col_width)
            line += f['modified'].ljust(modified_col_width)
            print(line)

    print('')
    return


def run_put(files, bucket):
    put_files(bucket, files, 'files')
    print('')

    return


def run_get(files, bucket):
    get_files(bucket, files, 'files')
    print('')

    return


def run_delete(files, bucket):
    filesToDelete = {}
    filesToDelete['files'] = {
        'bucket': bucket,
        'files': files,
        'prefix': ''
    }
    delete_files(filesToDelete)
    print('')

    return
