#!/usr/bin/python3
import boto3
from termcolor import colored
from time import sleep
from .common import run_lambda, SpinCursor, poll_build, get_log_stream_events


def run_build(args):
    if check_version(args.version):
        print('You are trying to build using the same version number again.')
        print('Please use another version number to build.')
        return False

    # Now always build desktop and ec along with platform
    ec = True
    if args.version:
        print('Triggering build...\n')
        return trigger_build(args.version, ec)

    return True

def check_version(version):
    version_used = False
    versions = run_lambda('paas-tools-lambda_get-versions')

    for version_in_lambda in versions['available']:
        existing_version = version_in_lambda.rsplit(',',1)[0]
        if version[0] == existing_version:
            version_used = True
            break

    return version_used

def trigger_build(version, ec):
    # Trigger codebuild and return result
    build_response = run_lambda('paas-tools-lambda_post-build',
                                {'build': 'paas-platform-build',
                                 'version': version[0],
                                 'ec': str(ec)})

    if 'error' in build_response:
        print(colored(build_response['error'], 'red'))
        return False
    else:
        buildId = build_response['buildId']

    sleep(3)
    status = poll_build(buildId)

    print(colored('Building platform, version: "'
          + version[0] + '"...', attrs=['bold']))

    spin = SpinCursor(msg='  Building...\t')
    spin.start()

    while True:
        sleep(5)
        status = poll_build(buildId)
        failedStates = [
            'FAILED',
            'FAULT',
            'TIMED_OUT',
            'STOPPED'
        ]
        if status['buildStatus'] == 'SUCCEEDED':
            spin.stop()
            spin.join()
            print(colored('\n  Build successfull!\n', 'green'))
            fetch_log(buildId)

            print(colored('To deploy a new version run "mztools deploy"\n',
                          attrs=['dark']))

            return True
        elif status['buildStatus'] in failedStates:
            spin.stop()
            spin.join()
            print(colored('\n  Build failed!\n', 'red'))
            fetch_log(buildId)
            return False

    return False


def fetch_log(buildId):
    print(colored('  Fetching logs', attrs=['bold']))
    print('    Waiting for log stream to close...30', end='', flush=True)
    seconds = 30
    while seconds > 0:
        sleep(1)
        if seconds == 20:
            print('...20', end='', flush=True)
        if seconds == 10:
            print('...10', end='', flush=True)
        seconds -= 1

    print('...done')
    print('    Fetching log stream...', end='', flush=True)
    logEvents = get_log_stream_events('/aws/codebuild/paas-platform-build')
    fileName = buildId.split(':', maxsplit=1)[1] + '.log'
    with open(fileName, 'w') as logFile:
        for line in logEvents:
            logFile.write(line + '\n')
    print('done')
    print('    Please see log: "' + fileName + '"\n')
