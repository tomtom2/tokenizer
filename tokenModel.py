#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import subprocess
import parser

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
LEMME_DB_PATH = CURRENT_PATH+'/../TP_MNTAL2013/lex80k.fr.utf8'

dico = parser.buildDicoWordLemme()
ignoredClasses = ['A']
probaLimit = 7

def mot_class_proba_liste():
    mots=[]
    classe=[]
    proba=[]
    os.chdir(CURRENT_PATH+"/../TP_MNTAL2013")
    p1 = subprocess.Popen(["cat", "input.txt"],stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["sh","./run_tokenizer.sh"],stdin=p1.stdout)
    trucmoche=open("output.txt","r")
    r=trucmoche.readline()

    while len(r.split("\t"))>=4:
        L=r.split("\t")
        mots.append(L[2])
        classe.append(L[3])
        proba.append(L[4].replace('\n', ''))
        r=trucmoche.readline()
    os.chdir(CURRENT_PATH)

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
    header = header.replace(', \n', '\n')
    myFile.write(header)
    for word in lemmes:
        myFile.write(word+': continuous.\n')
    myFile.close()

def setUpData():
    myFile = open('output/depeche.names', 'w')
    for d in parser.initialTextToList(CURRENT_PATH+'/../TP_MNTAL2013/corpus_depeche.txt'):
        dep = parser.Depeche(d)
        topic = dep.topic
        input_file = open(CURRENT_PATH+'/../TP_MNTAL2013/input.txt', 'w')
        input_file.write(dep.text)
        input_file.close()
        table = mot_class_proba_liste()
        print table[0]
        dep.setUpDictOfTerms(table, dico, ignoredClasses, probaLimit)
        line = ""
        for key in dep.occurences_dict:
            line += dep.occurences_dict[key]+', '
        line += dep.topic+'\n'
        myFile.write(line)
    myFile.close()

def renderResult():
    return

# os.chdir(CURRENT_PATH+"/../TP_MNTAL2013")
# corpus_test = CURRENT_PATH+'/../TP_MNTAL2013/corpus_test.txt'
# tokenizer = './run_tokenizer.sh'
# corpus = subprocess.Popen(['cat', corpus_test], stdout = subprocess.PIPE, )
# tokenized = subprocess.Popen(['sh', tokenizer], stdin = corpus.stdout, stdout = subprocess.PIPE)

# out = tokenized.communicate()
# print out
# os.chdir(CURRENT_PATH)


setUpNames()
setUpData()

print mot_class_proba_liste()[0]