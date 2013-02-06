#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import subprocess
import time
import parser

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
LEMME_DB_PATH = CURRENT_PATH+'/../TP_MNTAL2013/lex80k.fr.utf8'

dico = parser.buildDicoWordLemme()
ignoredClasses = ['DET', 'COCO', 'PREP', 'PREPDU']
probaLimit = 12


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

lemmes = []
for key in parser.getLemmeDico():
    lemmes.append(key)

def setUpNames():
    myFile = open('output/depeche.names', 'w')
    header = ', '.join(lemmes)+'\n'
    header = header.replace(', \n', '.\n')
    myFile.write(header)
    for word in lemmes:
        myFile.write(word+': continuous.\n')
    myFile.close()

def setUpData():
    total_start = time.time()
    myFile = open('output/depeche.data', 'w')
    print len(parser.initialTextToList(CURRENT_PATH+'/../TP_MNTAL2013/corpus_depeche.txt'))
    for d in parser.initialTextToList(CURRENT_PATH+'/../TP_MNTAL2013/corpus_depeche.txt')[0:10]:
        start = time.time()
        dep = parser.Depeche(d)
        topic = dep.topic
        input_file = open(CURRENT_PATH+'/../TP_MNTAL2013/input.txt', 'w')
        input_file.write(dep.text)
        input_file.close()
        table = mot_class_proba_liste()
        dep.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)
        line = ""
        for key in dep.occurences_dict:
            line = line + str(dep.occurences_dict[key])+', '
        line += dep.topic+'.\n'
        myFile.write(line)
        print "time="+str(time.time()-start)
        print ""
    myFile.close()
    print "TOTAL_TIME = "+str(time.time()-total_start)

def renderResult():
    return


setUpNames()
setUpData()
