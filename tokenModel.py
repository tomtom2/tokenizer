#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import subprocess
import time
import datetime
from timeout import timeout
import parser
import icsiboost_runner as icsi
import multiprocessing as mp
from subtokenizer import tokenize


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
LEMME_DB_PATH = CURRENT_PATH+'/../TP_MNTAL2013/lex80k.fr.utf8'
train_file_path = CURRENT_PATH+'/../TP_MNTAL2013/corpus_depeche.txt'
test_file_path = CURRENT_PATH+'/../TP_MNTAL2013/corpus_depeche.txt'
# train_file_path = CURRENT_PATH+'/../TP_MNTAL2013/material/train.txt'
# test_file_path = CURRENT_PATH+'/../TP_MNTAL2013/material/train.txt'

STEP_train = 15#30
STEP_test = 30#70
TIME_LIMIT = 90
force_rewrite = True

dico = parser.buildDicoWordLemme()
ignoredClasses = ['DET', 'COCO', 'PREP', 'PREPDU']
probaLimit = 50

lemmes = []
for key in parser.getLemmeDico():
    lemmes.append(key)
max_length_dict = 100000
max_length_dict = min(max_length_dict, len(lemmes))

def mot_class_proba_liste():
    mots=[]
    classe=[]
    proba=[]
    file_is_loaded = tokenize(TIME_LIMIT)
    if not file_is_loaded:
        return []
    trucmoche=open("../TP_MNTAL2013/output.txt","r")
    for r in trucmoche:
        r = r.replace('\n', '')
        if len(r.split("\t"))>4:
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
    header += '\n'
    header = header.replace(", \n", ".\n")
    print "HEADER: "+header
    myFile.write(header)
    for word in lemmes[0:max_length_dict]:
        myFile.write(word+': continuous.\n')
    myFile.close()


def write_data_row(depeche):
    line = ""
    start = time.time()
    topic = depeche.topic
    input_file = open(CURRENT_PATH+'/../TP_MNTAL2013/input.txt', 'w')
    input_file.write(depeche.text)
    input_file.close()
    print "loading data MOT_CLASS_PROBA from subprocess..."
    table = mot_class_proba_liste()
    if table == []:
        return ""
    print "start --> depeche.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)"
    depeche.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)
    print "DONE!"
    line_tmp = ""
    index = 0
    for lemme in lemmes[0:max_length_dict]:
        if lemme in depeche.occurences_dict:
            line_tmp = line_tmp + str(depeche.occurences_dict[lemme])+', '
        else:
            line_tmp = line_tmp + str(0)+', '
    line_tmp += depeche.topic+'.\n'
    depeche.clearDictOfTerms()
    print "time="+str(time.time()-start)+"\n"
    line = line_tmp
    return line_tmp

def setUpData():
    total_start = time.time()
    myFile = open('output/depeche.data', 'w')
    status = 0
    depeche_number = len(depeche_by_id)
    for dep_id in depeche_by_id:
        depeche = depeche_by_id[dep_id]
        status += 1
        print depeche.id+" ("+depeche.topic+") "+" learning="+str(status)+"/"+str(depeche_number)
        line = ""
        line = write_data_row(depeche)
        depeche.clearDictOfTerms()
        myFile.write(str(line))
    myFile.close()
    print "TOTAL_TIME = "+str(time.time()-total_start)


def write_test_row(depeche):
    start = time.time()
    topic = depeche.topic
    input_file = open(CURRENT_PATH+'/../TP_MNTAL2013/input.txt', 'w')
    input_file.write(depeche.text)
    input_file.close()
    table = mot_class_proba_liste()
    if table == []:
        return ""
    depeche.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)
    line = ""
    index = 0
    for lemme in lemmes[0:max_length_dict]:
        if lemme in depeche.occurences_dict:
            line = line + str(depeche.occurences_dict[lemme])+', '
        else:
            line = line + str(0)+', '
    if depeche.topic in depech_classes:
        print depeche.topic
        line += depeche.topic
    else:
        line += depech_classes.keys()[0]
    line += '.\n'
    depeche.clearDictOfTerms()
    print "time="+str(time.time()-start)+"\n"
    return line

def setUpTest(depeche_dico, alt_class):
    myFile = open('output/depeche.test', 'w')
    status = 0
    depeche_number = len(depeche_dico)
    for dep_id in depeche_dico:
        status += 1
        depeche = depeche_dico[dep_id]
        print depeche.id+"\tanalyse="+str(status)+"/"+str(depeche_number)
        # result = mp.Queue()
        # proc = mp.Process(target = write_test_row, args = (depeche, result))
        # proc.start()
        # proc.join(timeout = TIME_LIMIT)
        # if proc.is_alive():
        #     try:
        #         line = result.get()
        #     except:
        #         line = ""
        #         pass
        #     proc.terminate()
        #     if line == "":
        #         print "timeout!\n"
        # else:
        #     line = result.get()
        line = write_test_row(depeche)
        myFile.write(str(line))
        depeche.clearDictOfTerms()
    myFile.close()


if not os.path.exists('output/depeche.data') or force_rewrite:
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

if not os.path.exists('output/depeche.test') or force_rewrite:
    print "\n\n\n\n************************\n*** SETTING UP TESTS ***\n************************\n\n"
    setUpTest(depeche_by_id, alt_class)

print class_list
print "\n\n\n\n*************************\n*** RUNNING ICSIBOOST ***\n*************************\n\n"
print "Learning..."
icsi.run_learning(100)
print "Testing..."
icsi.result_classes(depeche_by_id, class_list)










##################################################################################################
##################################################################################################
#############################   BEEP   ###########################################################
##################################################################################################
##################################################################################################

# def beep(frequency, amplitude, duration):
#     sample = 8000
#     half_period = int(sample/frequency/2)
#     beep = chr(amplitude)*half_period+chr(0)*half_period
#     beep *= int(duration*frequency)
#     audio = file('/dev/audio', 'wb')
#     audio.write(beep)
#     audio.close()

# try:
#     beep(440, 63, 5)
# except:
#     pass

# cmd='beep -f100 -l1 '
# cmd=cmd + ' -n -f 440 -l5'

# os.system(cmd)