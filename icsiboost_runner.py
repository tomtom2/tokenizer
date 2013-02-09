#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import subprocess


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

def run_learning(iter_count):
    os.chdir(CURRENT_PATH+"/output")
    tokenized = subprocess.Popen(['../../icsiboost/src/icsiboost', '-S', './depeche', '-n', str(iter_count)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_str = ""
    stdout_lines = []
    stderr_lines = []
    while True:
        tokenized.poll()
        line = tokenized.stdout.readline()
        line = line.replace('\n', '')
        print line
        output_str += line+'\n'
        try:
            eline = tokenized.stderr.readline()
        except:
            eline = ""
        if line:
            stdout_lines.append(line)
        if eline:
            stderr_lines.append(eline)
            print eline
        if (line == "" and eline == "" and tokenized.returncode != None):
            break
    os.chdir(CURRENT_PATH)
    return output_str

def get_result_output():
    os.chdir(CURRENT_PATH+"/output")
    test_file = subprocess.Popen(['cat', './depeche.test'], stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    tokenized = subprocess.Popen(['../../icsiboost/src/icsiboost', '-S', './depeche', '-C'], stdin = test_file.stdout, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    
    output_str = ""
    stdout_lines = []
    stderr_lines = []
    while True:
        tokenized.poll()
        line = tokenized.stdout.readline()
        line = line.replace('\n', '')
        if line!="":
            print line
        output_str += line+'\n'
        try:
            eline = tokenized.stderr.readline()
        except:
            eline = ""
        if line:
            stdout_lines.append(line)
        if eline:
            stderr_lines.append(eline)
            if eline!="":
                print eline
        if (line == "" and eline == "" and
            tokenized.returncode != None):
            break
    os.chdir(CURRENT_PATH)
    return output_str

def get_class_index():
    index_list = []
    class_output = get_result_output()
    response_list = class_output.split('\n')
    for line in response_list:
        l = line.split(" ")
        has_class = False
        for i in range(len(l)):
            if l[i] == "1":
                index_list.append(i)
                has_class = True
        if not has_class:
            index_list.append(-1)
    return index_list


def result_classes(dico,class_list):
    id_list = []
    true_class_list = []
    estimation_list = []
    class_index = get_class_index()

    index = 0
    for pk in dico:
        id_list.append(pk)
        true_class_list.append(dico[pk].topic)
        if class_index[index]<len(class_list) and class_index[index]!=-1:
            estimation_list.append(class_list[class_index[index]])
        else:
            estimation_list.append("?")
        index += 1
    performence = 0
    f=open('classification_result.txt', 'w')
    for i in range(len(id_list)):
        if true_class_list[i]==estimation_list[i]:
            performence += 1
        else:
            print id_list[i]+"\t"+true_class_list[i]+"\t"+estimation_list[i]
        f.write('<doc id="'+id_list[i]+'" topic="'+estimation_list[i]+'">\n')
    performence = performence*100.0/len(id_list)
    f.write("==> "+str(performence)+"% correct! <==")
    print str(performence)[0:4]+"% correct!"
    f.close()

if __name__=='__main__':
    run_learning(5)
    print get_class_index()