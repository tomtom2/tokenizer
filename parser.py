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
        my_lemme_dico[line[0]] = line[3].replace('\n', '')
    my_file.close()
    while '|' in my_lemme_dico:
        del my_lemme_dico['|']
    return my_lemme_dico

def getLemmeDico():
    my_lemme_dico = {}
    my_file = open(LEMME_DB_PATH, 'r')
    for line in my_file:
        line = line.split(" ")
        my_lemme_dico[line[3].replace('\n', '')] = 0
    my_file.close()
    while '|' in my_lemme_dico:
        del my_lemme_dico['|']
    return my_lemme_dico


def initialTextToList(file_path):
    listeDepeches = []
    depeche = ""
    my_file = open(file_path, 'r')
    for line in my_file:
        if line.startswith("<doc") and not depeche == "" and not line == "\n":
            listeDepeches.append(depeche)
            depeche = ""
        depeche += line
    my_file.close()
    if not depeche == "":
        listeDepeches.append(depeche)
    return listeDepeches


def get_Id(depeche):
    regex = r'<doc id="(.+)" (.*)>'
    m = re.match(regex, depeche)
    return m.group(1)
def get_Topic(depeche):
    regex = r'<doc id="(.+)" topic="(.+)">'
    m = re.match(regex, depeche)
    if m:
        return m.group(2)
    return ""


class Depeche(object):
    def __init__(self, depeche):
        self.occurences_dict = getLemmeDico()
        self.id = get_Id(depeche)
        self.__name__=self.id
        self.topic = get_Topic(depeche).replace(',', '').replace(' ', '_')
        text = ""
        try:
            depeche = str(depeche)
        except:
            print self.id
        for line in depeche.split('\n'):
            if not line.startswith("<doc") and not line == "</doc>" and not line == '':
                line = "<s>"+line.lower()+"</s>\n"
                text += line
        self.text = text

    def setUpDictOfTerms(self, table, dico, ignoredClasses, probaLimit):
        for i in range(len(table)):
            total = 0
            if table[i][0] in dico and not table[i][1] in ignoredClasses and float(table[i][2])<probaLimit:
                self.occurences_dict[dico[table[i][0]]] += 1
                total += 1
            if total == 0:
                break
            for key in self.occurences_dict:
                self.occurences_dict[key] = self.occurences_dict[key]*1000/total
    def clearDictOfTerms(self):
        self.occurences_dict = {}

if __name__=='__main__':
    for d in initialTextToList(CURRENT_PATH+'/../TP_MNTAL2013/corpus_depeche.txt')[0:3]:
        dep = Depeche(d)
        topic = dep.topic
        print topic
        print d[0:60]
        id = dep.id
    print get_Topic('<doc id="id" topic="coucou">')
    print get_Topic('<doc id="id">')