#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import signal
import subprocess, threading

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

class Command(object):
    def __init__(self):
        self.process1 = None
        self.process2 = None

    def run(self, timeout=90):
        def target():
            print 'Thread started'
            os.chdir(CURRENT_PATH+"/../TP_MNTAL2013")
            input_file = CURRENT_PATH+'/../TP_MNTAL2013/input.txt'
            tokenizer = './run_tokenizer.sh'
            self.process1 =  subprocess.Popen(['cat', input_file], stdout = subprocess.PIPE)#subprocess.Popen(self.cmd, shell=True)
            self.process2 = subprocess.Popen(['sh', tokenizer], stdin = self.process1.stdout, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
            
            my_stdout_file = open("output.txt", "w")
            stdout_lines = []
            stderr_lines = []
            while True:
                self.process2.poll()
                line = self.process2.stdout.readline()
                print line.replace("\n", "")
                my_stdout_file.write(line)
                try:
                    eline = self.process2.stderr.readline()
                except:
                    eline = ""
                if line:
                    stdout_lines.append(line)
                if eline:
                    print eline.replace("\n", "")
                    stderr_lines.append(eline)
                    print eline
                    try:
                        os.kill(-self.process2.pid, signal.SIGKILL)
                        return []
                    except:
                        break
                if (line == "" and eline == "" and
                    self.process2.returncode != None):
                    break
            my_stdout_file.close()

            os.chdir(CURRENT_PATH)
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process2.terminate()
            thread.join()
            try:
                thread._Thread__stop()
                print "Thread stopped"
            except:
                print(str(thread.getName()) + ' could not be terminated')
            print "Process terminated!"
        print self.process2.returncode

# command = Command()
# command.run(3)













def tokenize(timeout=90):
    print "Starting tokenization..."
    os.chdir(CURRENT_PATH+"/../TP_MNTAL2013")
    input_file = CURRENT_PATH+'/../TP_MNTAL2013/input.txt'
    tokenizer = './run_tokenizer.sh'
    process1 =  subprocess.Popen(['cat', input_file], stdout = subprocess.PIPE)#subprocess.Popen(self.cmd, shell=True)
    process2 = subprocess.Popen(['sh', tokenizer], stdin = process1.stdout, stdout = subprocess.PIPE, stderr=subprocess.PIPE)

    my_stdout_file = open("output.txt", "w")
    stdout_lines = []
    stderr_lines = []

    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
    try:
        while True:
            process2.poll()
            line = process2.stdout.readline()
            my_stdout_file.write(line)
            try:
                eline = self.process2.stderr.readline()
            except:
                eline = ""
            if line:
                stdout_lines.append(line)
            if eline:
                print eline.replace("\n", "")
                stderr_lines.append(eline)
                print eline
                try:
                    os.kill(-self.process2.pid, signal.SIGKILL)
                except:
                    break
            if (line == "" and eline == "" and
                process2.returncode != None):
                break
            signal.alarm(0)
    except Alarm:
        print "Timeout!\n"
        my_stdout_file.close()
        return False
    my_stdout_file.close()

    os.chdir(CURRENT_PATH)
    print 'Thread finished'
    return True

if __name__=='__main__':
    tokenize(3)
    tokenize(90)