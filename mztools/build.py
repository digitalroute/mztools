#!/usr/bin/python3
import boto3
from termcolor import colored
from time import sleep
from .common import run_lambda, SpinCursor, poll_build, get_log_stream


def run_build(args):

    if args.no_ec:
        ec = False
    else:
        ec = True

    if args.version:
        print('Triggering build...\n')
        trigger_build(args.version, ec)

    return


def trigger_build(version, ec):
    # Trigger codebuild and return result
    build_response = run_lambda('paas-tools-lambda_post-build',
                                {'build': 'paas-platform-build',
                                 'version': version[0],
                                 'ec': ec})

    if 'error' in build_response:
        print(colored(build_response['error'], 'red'))
        return
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

            break
        elif status['buildStatus'] in failedStates:
            spin.stop()
            spin.join()
            print(colored('\n  Build failed!\n', 'red'))
            fetch_log(buildId)
            break

    return


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
    logEvents = get_log_stream('/aws/codebuild/paas-platform-build')
    fileName = buildId.split(':', maxsplit=1)[1] + '.log'
    with open(fileName, 'w') as logFile:
        for line in logEvents:
            logFile.write(line + '\n')
    print('done')
    print('    Please see log: "' + fileName + '"\n')
