#!/usr/local/EagleEP/bin/python
import subprocess, signal
import shlex
import argparse
import os
import sys
sys.path.append('/usr/local/EagleEP')
from plogical.EagleEPLogFileWriter import EagleEPLogFileWriter as logging


class policyCTRL:
    applicationPath = '/usr/local/EagleEP/postfixSenderPolicy/pid'
    cleaningPID = '/usr/local/EagleEP/postfixSenderPolicy/cpid'

    def prepareArguments(self):

        parser = argparse.ArgumentParser(description='EaglePanel Policy Control Parser!')
        parser.add_argument('function', help='Specific a operation to perform!')

        return parser.parse_args()

    def start(self):

        if os.path.exists(policyCTRL.applicationPath):
            self.stop()

        command = '/usr/local/EagleEP/postfixSenderPolicy/startServer.py'
        subprocess.Popen(shlex.split(command))

    def stop(self):

        path = policyCTRL.applicationPath
        if os.path.exists(path):
            pid = open(path, "r").readlines()[0]
            try:
                os.kill(int(pid), signal.SIGTERM)
            except BaseException as msg:
                logging.writeToFile(str(msg))



def main():

    policy = policyCTRL()
    args = policy.prepareArguments()

    ## Website functions

    if args.function == "start":
        policy.start()
    elif args.function == "stop":
        policy.stop()
    elif args.function == "restart":
        policy.stop()
        policy.start()

if __name__ == "__main__":
    main()