#!/usr/bin/python3
# coding=utf-8

import json
import threading
import sys
import os
import time
import shutil
import tempfile

import boto3
import botocore

from datetime import datetime
from termcolor import colored
from .ver import __version__


class SpinCursor(threading.Thread):
    """ A console spin cursor class """

    def __init__(self, msg='', speed=2):
        # Count of a spin
        self.count = 0
        self.out = sys.stdout
        self.flag = False
        # Any message to print first ?
        self.msg = msg
        # Complete printed string
        self.string = ''
        # Speed is given as number of spins a second
        # Use it to calculate spin wait time
        self.waittime = 1.0/float(speed*4)
        try:
            if os.environ["PYTHONIOENCODING"] == 'utf-8':
                self.spinchars = ("◴", "◷", "◶", "◵")
        except KeyError:
            self.spinchars = ('- ', '\ ', '| ', '/ ')

        threading.Thread.__init__(self, None, None, "Spin Thread")

    def spin(self):
        """ Perform a single spin """

        for x in self.spinchars:
            self.string = self.msg + x + "\r"
            self.out.write(self.string)
            self.out.flush()
            time.sleep(self.waittime)

    def run(self):

        while not self.flag:
            self.spin()
            self.count += 1

        # Clean up display...
        self.out.write(" "*(len(self.string) + 1))

    def stop(self):
        self.flag = True


def poll_build(buildid):
    # Poll AWS CLI for status of build/deploy
    response = run_lambda('paas-tools-lambda_get-build', {
        'buildid': buildid
    })

    return(json.loads(response))


def get_bucket_name(ssmParam):
    try:
        ssmClient = boto3.client('ssm')
        response = ssmClient.get_parameter(
            Name=ssmParam,
            WithDecryption=False
        )
    except botocore.exceptions.ClientError as e:
        print('Not allowed to read from cloud, have you assumed the correct role?')
        print('AWS Error: ', e)
        sys.exit(1)

    return(response['Parameter']['Value'])


def get_repo_bucket():
    return(get_bucket_name('tools-bucket'))


def get_extrefs_bucket():
    return(get_bucket_name('extrefs-bucket'))


def get_general_bucket():
    return(get_bucket_name('paas-general-bucket'))


def check_response_version(response):

    # Do we have an incompatible string in the response?
    if 'mztools_version' in response:
        resp = json.loads(response)
        print('Not allowed to trigger backend, mztools is out of date.')
        print('Current version: ' + __version__)
        print('Required version: ' + resp['mztools_version'])
        sys.exit(1)

    # We return  if "mztools_version" is not in the response
    return

def run_lambda(function, payload={}):
    # Append mztools version
    payload['mztools_version'] = __version__

    try:
        lmb = boto3.client('lambda')
        response = lmb.invoke(
            FunctionName=function,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=json.dumps(payload)
        )
    except botocore.exceptions.PartialCredentialsError as e:
        print('Not allowed to trigger backend, have you assumed the correct role?')
        print('AWS Error: ', e)
        sys.exit(1)

    # Load the response, decoded with json
    json_response = json.loads(response['Payload'].read().decode("utf-8"))

    # Check for invalid version first
    check_response_version(json_response)

    return json_response


def get_log_stream(logGroup, prefix=None):
    client = boto3.client('logs')

    # Get last log stream or prefixed log stream
    if prefix:
        response = client.describe_log_streams(
            logGroupName=logGroup,
            logStreamNamePrefix=prefix,
            limit=1
        )
    else:
        response = client.describe_log_streams(
            logGroupName=logGroup,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )

    try:
        logStream = response['logStreams'][0]['logStreamName']
    except IndexError:
        print(colored('  Log not found!\n', 'red'))
        return()

    # Get log events
    response = client.get_log_events(
        logGroupName=logGroup,
        logStreamName=logStream,
        startFromHead=False
        )

    # Add all formatted lines to a list of lines
    logEvents = []
    for event in response['events']:
        timeStamp = datetime.fromtimestamp(event['timestamp']/1000.0)\
            .strftime('%c')
        logEvents.append("{} - {}".format(
            timeStamp,
            event['message'].rstrip('\n')
            )
        )

    return(logEvents)


def get_file_list(bucket, prefixList=None):
    # Invoke list lambda tp get current uploaded versions
    filesDict = run_lambda('paas-tools-lambda_get-list',
        {'bucket': bucket, 'prefix': prefixList}
    )

    return(filesDict)


def put_files(bucket, files, prefix):
    s3 = boto3.resource('s3')

    print(colored('  ' + prefix.capitalize() + ':', attrs=['bold']))

    for fileName in files:
        print('    ' + fileName, end='')
        data = open(fileName, 'rb')
        fileNameNoPath = fileName.split('/')[-1]
        if prefix == 'files':
            key = fileNameNoPath
        else:
            key = 'repo/' + prefix + '/' + fileNameNoPath
        try:
            s3.Bucket(bucket).put_object(Key=key, Body=data)
            print(colored('\tok', 'green'))
        except botocore.exceptions.ClientError as e:
            print(colored('\tfailed', 'red'))

    return


def put_folder(bucket, folders, prefix):
    tempDir = tempfile.gettempdir()

    for folder in folders:
        fileName = tempDir + '/' + folder.split('/')[-1]
        shutil.make_archive(fileName, 'zip', folder)
        put_files(bucket, [fileName + '.zip'], prefix)

    return


def get_files(bucket, files, prefix):
    s3 = boto3.resource('s3')

    print(colored('  ' + prefix.capitalize() + ':', attrs=['bold']))

    for fileName in files:
        print('    ' + fileName, end='')
        if prefix == 'files':
            key = fileName
        else:
            key = 'repo/' + prefix + '/' + fileName
        try:
            s3.Bucket(bucket).download_file(key, fileName)
            print(colored('\tok', 'green'))
        except botocore.exceptions.ClientError as e:
            print(colored('\tfailed', 'red'))

    return


def delete_files(filesToDelete):
    # Bool to keep track of if we have any files to delete
    staged = False

    # Verify/stage files
    stagedFilesToDelete = run_delete_operation(filesToDelete)

    # List all files, staged or not found
    for fileType in stagedFilesToDelete:
        print(colored('  ' + fileType.capitalize() + ':', attrs=['bold']))
        try:
            if stagedFilesToDelete[fileType]['files']:
                staged = True
                print('    Staged for deletion:')
                for f in stagedFilesToDelete[fileType]['files']:
                    print(colored('      ' + f, 'yellow'))
        except KeyError:
            pass

        try:
            if stagedFilesToDelete[fileType]['notfound']:
                print('    Not found:')
                for f in stagedFilesToDelete[fileType]['notfound']:
                    print(colored('      ' + f, 'red'))
        except KeyError:
            pass

        print('')

    # If we have files to delete, ask the question
    if staged:
        question = 'Are you sure you want to delete these files? '
        question += '[yes/no]: '
        verification = input(question)
        while verification != 'yes':
            if verification == 'no':
                sys.exit(0)
            print('Please answer "yes" or "no"')
            verification = input(question)

        print('Deleting files...\n')

        # Delete the actual files
        actualFilesToDelete = run_delete_operation(filesToDelete, True)

        for fileType in actualFilesToDelete:
            print(colored('  ' + fileType.capitalize() + ':', attrs=['bold']))
            try:
                if actualFilesToDelete[fileType]['files']:
                    print('    Deleted:')
                    for f in actualFilesToDelete[fileType]['files']:
                        print(colored('      ' + f, 'green'))
            except KeyError:
                pass

            try:
                if actualFilesToDelete[fileType]['notfound']:
                    print('    Not deleted:')
                    for f in actualFilesToDelete[fileType]['notfound']:
                        print(colored('      ' + f, 'red'))
            except KeyError:
                pass
    else:
        print('Nothing to delete\n')
        return

    return


def run_delete_operation(filesDict, verified=False):

    filesOperated = {}

    for fileType in filesDict:
        # Update dict with what files to delete
        response = run_lambda('paas-tools-lambda_post-delete', {
            'bucket': filesDict[fileType]['bucket'],
            'prefix': filesDict[fileType]['prefix'],
            'files': filesDict[fileType]['files'],
            'verified': verified
            })

        filesOperated[fileType] = response

    return(filesOperated)
