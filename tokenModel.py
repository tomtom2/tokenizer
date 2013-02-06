#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import subprocess
import time
import parser

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
LEMME_DB_PATH = CURRENT_PATH+'/../TP_MNTAL2013/lex80k.fr.utf8'
train_file_path = CURRENT_PATH+'/../TP_MNTAL2013/material/train.txt'
test_file_path = CURRENT_PATH+'/../TP_MNTAL2013/material/test.txt'

dico = parser.buildDicoWordLemme()
ignoredClasses = ['DET', 'COCO', 'PREP', 'PREPDU']
probaLimit = 12

lemmes = []
for key in parser.getLemmeDico():
    lemmes.append(key)
max_length_dict = 10000
max_length_dict = min(max_length_dict, len(lemmes))
print max_length_dict

def mot_class_proba_liste():
    mots=[]
    classe=[]
    proba=[]
    os.chdir(CURRENT_PATH+"/../TP_MNTAL2013")
    input_file = CURRENT_PATH+'/../TP_MNTAL2013/input.txt'
    tokenizer = './run_tokenizer.sh'
    corpus = subprocess.Popen(['cat', input_file], stdout = subprocess.PIPE)
    tokenized = subprocess.Popen(['sh', tokenizer], stdin = corpus.stdout, stdout = subprocess.PIPE, stderr=subprocess.PIPE)

    my_stdout_file = open("output.txt", "w")
    stdout_lines = []
    stderr_lines = []
    while True:
        tokenized.poll()
        line = tokenized.stdout.readline()
        my_stdout_file.write(line)
        try:
            eline = tokenized.stderr.readline()
        except:
            eline = ""
        if line:
            stdout_lines.append(line)
        if eline:
            stderr_lines.append(eline)
        if (line == "" and eline == "" and
            tokenized.returncode != None):
            break
    my_stdout_file.close()
    os.chdir(CURRENT_PATH)

    trucmoche=open("../TP_MNTAL2013/output.txt","r")
    r=trucmoche.readline()
    for r in trucmoche:
        r = r.replace('\n', '')
        if len(r.split("\t"))>=4:
            L=r.split("\t")
            mots.append(L[2])
            classe.append(L[3])
            proba.append(L[4])
    trucmoche.close()
    table = []
    for i in range(len(mots)):
        table.append([mots[i], classe[i], proba[i]])
    return table

depeche_by_id = {}
for d in parser.initialTextToList(train_file_path)[0:3]:
    dep = parser.Depeche(d)
    depeche_by_id[dep.id] = dep

depech_classes = {}
for dep_id in depeche_by_id:
    dep = depeche_by_id[dep_id]
    if dep.topic in depech_classes:
        depech_classes[dep.topic] += 1
    else:
        depech_classes[dep.topic] = 0


def setUpNames():
    myFile = open('output/depeche.names', 'w')
    header = ""
    for key in depech_classes:
        header += key+", "
    header += '.\n'
    header = header.replace(', .\n', '.\n')
    print header
    myFile.write(header)
    for word in lemmes[0:max_length_dict]:
        print word
        myFile.write(word+': continuous.\n')
    myFile.close()

def setUpData():
    total_start = time.time()
    myFile = open('output/depeche.data', 'w')
    print len(parser.initialTextToList(train_file_path))
    for dep_id in depeche_by_id:
        start = time.time()
        dep = depeche_by_id[dep_id]
        print dep.id
        topic = dep.topic
        input_file = open(CURRENT_PATH+'/../TP_MNTAL2013/input.txt', 'w')
        input_file.write(dep.text)
        input_file.close()
        table = mot_class_proba_liste()
        dep.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)
        line = ""
        index = 0
        for lemme in lemmes[0:max_length_dict]:
            if lemme in dep.occurences_dict:
                line = line + str(dep.occurences_dict[lemme])+', '
            else:
                line = line + str(0)+', '
        # for key in dep.occurences_dict:
        #     index += 1
        #     line = line + str(dep.occurences_dict[key])+', '
        #     if index >= max_length_dict:
        #         break
        line += dep.topic+'.\n'
        myFile.write(line)
        print "time="+str(time.time()-start)
        print ""
    myFile.close()
    print "TOTAL_TIME = "+str(time.time()-total_start)

def setUpTest():
    myFile = open('output/depeche.test', 'w')
    for dep_id in depeche_by_id:
        start = time.time()
        dep = depeche_by_id[dep_id]
        print dep.id
        topic = dep.topic
        input_file = open(CURRENT_PATH+'/../TP_MNTAL2013/input.txt', 'w')
        input_file.write(dep.text)
        input_file.close()
        table = mot_class_proba_liste()
        dep.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)
        line = ""
        index = 0
        for lemme in lemmes[0:max_length_dict]:
            if lemme in dep.occurences_dict:
                line = line + str(dep.occurences_dict[lemme])+', '
            else:
                line = line + str(0)+', '
        # for key in dep.occurences_dict:
        #     index += 1
        #     line = line + str(dep.occurences_dict[key])+', '
        #     if index >= max_length_dict:
        #         break
        line += dep.topic+'.\n'
        myFile.write(line)
        print "time="+str(time.time()-start)
        print ""
    myFile.close()

def result_classes(dico,file):
    f=open(file, 'r')
    result=[]
    L = list(dico.keys())
    r=f.readline()

    while r!="":
        list_line=r.split()
        for i in range(0,6):
            if r[i]==1:
                result.append(L[i])
                break
        r=f.readline()
    return result 


setUpNames()
setUpData()

for d in parser.initialTextToList(test_file_path)[0:3]:
    dep = parser.Depeche(d)
    depeche_by_id[dep.id] = dep

setUpTest()
