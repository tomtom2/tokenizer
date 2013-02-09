#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import subprocess
import time
from timeout import timeout
import parser
import icsiboost_runner as icsi


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
LEMME_DB_PATH = CURRENT_PATH+'/../TP_MNTAL2013/lex80k.fr.utf8'
train_file_path = CURRENT_PATH+'/../TP_MNTAL2013/corpus_depeche.txt'
test_file_path = CURRENT_PATH+'/../TP_MNTAL2013/material/test.txt'

test_file_path = train_file_path

STEP_train = 1
STEP_test = 8

dico = parser.buildDicoWordLemme()
ignoredClasses = ['DET', 'COCO', 'PREP', 'PREPDU']
probaLimit = 12

lemmes = []
for key in parser.getLemmeDico():
    lemmes.append(key)
max_length_dict = 10000
max_length_dict = min(max_length_dict, len(lemmes))

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
for d in parser.initialTextToList(train_file_path)[0::STEP_train]:
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
    header += 'X.\n'
    print "HEADER: "+header
    myFile.write(header)
    for word in lemmes[0:max_length_dict]:
        myFile.write(word+': continuous.\n')
    myFile.close()


@timeout(90)
def write_data_row(depeche):
    start = time.time()
    topic = depeche.topic
    input_file = open(CURRENT_PATH+'/../TP_MNTAL2013/input.txt', 'w')
    input_file.write(depeche.text)
    input_file.close()
    print "loadding data MOT_CLASS_PROBA from subprocess..."
    table = mot_class_proba_liste()
    print "start --> depeche.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)"
    depeche.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)
    print "DONE!"
    line = ""
    index = 0
    for lemme in lemmes[0:max_length_dict]:
        if lemme in depeche.occurences_dict:
            line = line + str(depeche.occurences_dict[lemme])+', '
        else:
            line = line + str(0)+', '
    line += depeche.topic+'.\n'
    depeche.clearDictOfTerms()
    print "time="+str(time.time()-start)
    return line

def setUpData():
    total_start = time.time()
    myFile = open('output/depeche.data', 'w')
    status = 0
    depeche_number = len(depeche_by_id)
    for dep_id in depeche_by_id:
        depeche = depeche_by_id[dep_id]
        status += 1
        print depeche.id+" ("+depeche.topic+") "+" learning="+str(status)+"/"+str(depeche_number)
        line = write_data_row(depeche)
        depeche.clearDictOfTerms()
        myFile.write(str(line))
    myFile.close()
    print "TOTAL_TIME = "+str(time.time()-total_start)

@timeout(90)
def write_test_row(depeche):
    start = time.time()
    topic = depeche.topic
    input_file = open(CURRENT_PATH+'/../TP_MNTAL2013/input.txt', 'w')
    input_file.write(depeche.text)
    input_file.close()
    table = mot_class_proba_liste()
    depeche.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)
    line = ""
    index = 0
    for lemme in lemmes[0:max_length_dict]:
        if lemme in depeche.occurences_dict:
            line = line + str(depeche.occurences_dict[lemme])+', '
        else:
            line = line + str(0)+', '
    if depeche.topic in depech_classes:
        line += depeche.topic
    else:
        line += 'X'
    line += '.\n'
    line = line.replace(', \n', '.\n')
    depeche.clearDictOfTerms()
    print "time="+str(time.time()-start)
    return line

def setUpTest(depeche_dico, alt_class):
    myFile = open('output/depeche.test', 'w')
    status = 0
    depeche_number = len(depeche_dico)
    for dep_id in depeche_dico:
        status += 1
        depeche = depeche_dico[dep_id]
        print depeche.id+"\tanalyse="+str(status)+"/"+str(depeche_number)
        line = write_test_row(depeche)
        myFile.write(str(line))
        depeche.clearDictOfTerms()
    myFile.close()


if not os.path.exists('output/depeche.data') or True:
    print "\n\n\n\n***********************\n*** SETTING UP DATA ***\n***********************\n\n"
    setUpNames()
    setUpData()

depeche_by_id = {}
for d in parser.initialTextToList(test_file_path)[0::STEP_test]:
    dep = parser.Depeche(d)
    depeche_by_id[dep.id] = dep


class_list=[]
for key in depech_classes:
    class_list.append(key)

alt_class = " ".join(class_list)

if not os.path.exists('output/depeche.test') or True:
    print "\n\n\n\n************************\n*** SETTING UP TESTS ***\n************************\n\n"
    setUpTest(depeche_by_id, alt_class)

print class_list
print "\n\n\n\n*************************\n*** RUNNING ICSIBOOST ***\n*************************\n\n"
print "Learning..."
icsi.run_learning(10)
print "Testing..."
icsi.result_classes(depeche_by_id, class_list)
