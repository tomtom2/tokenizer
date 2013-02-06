#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import re

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
LEMME_DB_PATH = CURRENT_PATH+'/../TP_MNTAL2013/lex80k.fr.utf8'

def buildDicoWordLemme():
    my_lemme_dico = {}
    my_file = open(LEMME_DB_PATH, 'r')
    for line in my_file:
        line = line.split(" ")
        my_lemme_dico[line[0]] = line[3]
    my_file.close()
    return my_lemme_dico

def getLemmeDico():
    my_lemme_dico = {}
    my_file = open(LEMME_DB_PATH, 'r')
    for line in my_file:
        line = line.split(" ")
        my_lemme_dico[line[3].replace('\n', '')] = 0
    my_file.close()
    return my_lemme_dico


def initialTextToList(file_path):
    listeDepeches = []
    depeche = ""
    my_file = open(file_path, 'r')
    for line in my_file:
        if line.startswith("<doc") and not depeche == "":
            listeDepeches.append(depeche)
            depeche = ""
        depeche += line
    my_file.close()
    if not depeche == "":
        listeDepeches.append(depeche)
    return listeDepeches


def get_Id_Topic(depeche):
    regex = r'<doc id="(.+)" topic="(.+)">'
    m = re.match(regex, depeche)
    return [m.group(1), m.group(2)]


class Depeche(object):
    def __init__(self, depeche):
        self.occurences_dict = getLemmeDico()
        idAndTopic = get_Id_Topic(depeche)
        self.id = idAndTopic[0]
        self.topic = idAndTopic[1]
        text = ""
        for line in depeche:
            if not line.startswith("<doc") and not line == "</doc>":
                line = "<s>"+line.replace("\n", "").lower()+"</s>\n"
                text += line
        self.text = text

    def setUpDictOfTerms(self, table, dico, ignoredClasses, probaLimit):
        for i in range(len(table)):
            print table[i]
            if table[0] in dico and not table[1] in ignoredClasses and float(str(table[2]))<probaLimit:
                self.occurences_dict[dico[table[0]]] += 1

if __name__=='__main__':
    for d in initialTextToList(CURRENT_PATH+'/../TP_MNTAL2013/corpus_depeche.txt'):
        dep = Depeche(d)
        topic = dep.topic
        id = dep.id
        print id+": "+topic