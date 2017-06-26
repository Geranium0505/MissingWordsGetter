#! /usr/bin/env python
# coding:utf-8

import sys
import MeCab
import os.path
import codecs
import subprocess
import unicodedata
import re
import treetaggerwrapper
from collections import Counter
#from functools import reduce
from operator import add

langtype = 'ja'

def is_japanese(string):
    string = unicode(string,'utf-8',errors='ignore')
    for ch in string:
        try:
            name = unicodedata.name(ch)
        except ValueError:
            name = ""
        finally:
            if "CJK UNIFIED" in name \
                or "HIRAGANA" in name \
                    or "KATAKANA" in name:
                        return True

    return False

def ReadFile(filepass):
    try:
        File = open(filepass, 'r')
    except IOError:
        print('!--IOError--!')
        return
    rawtexts = File.read()
    File.close()
    return rawtexts


def JoinPass(filename, Pass):
    return Pass + '/' + filename


def GetAllFileName(dirname):
    fileNameList = os.listdir(dirname)
    for filename in fileNameList:
        if '~' in filename:
            fileNameList.remove(filename)
    fileNameList.sort()
    for filename in fileNameList:
        print(filename)
    return fileNameList


def ExtractNoun(text,Type):
    tagger = MeCab.Tagger('-ochasen')
    tagger.parse('')
    text = text.replace(' ', '')
    text = text.replace('　', '')

    node = tagger.parseToNode(text)
    Nouns = []
    while node:
        # if node.feature.split(",")[0] == '名詞' or node.feature.split(",")[0]
        # == '動詞':
        if Type != "NOUN":
            if node.feature.split(',')[0] == '動詞' or node.feature.split(',')[0] == '形容詞':
            # print (node.surface,node.feature.split(",")[6],node.feature)
                Nouns.append(node.feature.split(',')[6])
        if node.feature.split(',')[0] == '名詞':
            Nouns.append(node.surface)
        node = node.next
    return Nouns


def ExtractNoun_en(text):
    text = unicode(text,errors='ignore')
    text = text.lower()
    text= text.replace(':',' ').replace('*',' ')
    tagdir = 'treetagger/'
    tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR=tagdir)
    lines = tagger.TagText(text)
    tmp = []
    parts = []

    for line in lines:
        tmp = line.split('\t')
        escapeList = ['CC', 'DT', 'CD', 'EX', 'FW', 'LS', 'RB', 'TO', 'SENT',
                      'IN', 'SYM', 'PP', 'PP$', 'PBR', 'PBS', 'MD', '(', ')', ',',
                      'VB', 'VBD', 'VBG', 'VBN', 'VBZ', 'VD', 'VDD', 'VDG', 'VDN', 'VDP',
                      'VH', 'VHD', 'VHG', 'VHN', 'VHZ', 'VHP', 'WDT', 'WP', 'WP$', 'WRB',
                      ':', '$']
        #print (line,tmp[1],len(lines))
        if not(tmp[1] in escapeList):
            parts.append(tmp[2])
            #print(tmp[1], tmp[2])
    return parts


def ListtoDict(List):
    dictionary = {}
    counter = Counter(List)
    for word, cnt in counter.most_common():
        dictionary.update({word: cnt})
    return dictionary


def FiletoDict(filename):
    List = []
    dictionary = {}
    addedDict = {}

    File = open(filename, 'r')
    rows = File.readlines()
    File.close()

    for row in rows:
        List = row.split()
        addedDict = {List[0]: List[1]}
        dictionary.update(addedDict)
    return dictionary


def SieveWord(List):
    NewList = []

    for word in List:
        if judgment(word):
            NewList.append(word)
        else:
            pass
    return NewList


def judgment(word):
    if word.isdigit() is False:
        if not (('.....' in word)or('---'in word)
                or('（'in word)or('）'in word)):
            if len(word) > 1:
                return True
    return False


def FilestoLines(dirname, langoption=''):
    filenameList = []
    filepassList = []
    filetextList = []
    pre_langtype = ""

    if 'txt' in dirname:
        filenameList.append(dirname)
        filepassList.append(dirname)
    else:
        filenameList = GetAllFileName(dirname)
        filepassList = list(map(lambda x: JoinPass(x, dirname), filenameList))
    filetextList = list(map(lambda x: ReadFile(x), filepassList))

    linesList = []
    num = len(filetextList)
    for i in range(num):
        if langoption != '':
            langtype = langoption
        elif is_japanese(filetextList[i]) == True:
            langtype = 'ja'
        else:
            langtype = 'en'
        print filenameList[i],'...lang',langtype
        if i > 0 and pre_langtype != langtype:
            raise KeyError
        else:
            pre_langtype = langtype
            TexttoLines(filetextList[i], linesList,langtype)
    return linesList,langtype


def GetWords(linesList,Type,langtype):
    wordList = []
    freqDicts = {}

    print "\nNow analysing..."

    for i,line in enumerate(linesList):
        i = i + 1
        if langtype == 'ja':
            wordList.append(ExtractNoun(line,Type))
        else:
            wordList.append(ExtractNoun_en(line))
        sys.stdout.write("\r%d" % i)
        sys.stdout.write("/%d" % len(linesList))      
        sys.stdout.flush()
  
    flatwordList = reduce(add,wordList)
    return wordList

def TexttoLines(text, lineList,langtype):
    tmp = []
    if langtype == 'ja':
        tmp = re.split('\n\n|。|\.', text)
    else:
        #tmp = re.split('\n\n|\.', text)
        tmp = re.split('==>.+<==',text)
#    tmp = re.split('\n\n\n', text)
    tmp = list(map((lambda s: s.replace('\n', '')), tmp))
    tmp = list(filter(lambda s: s != '', tmp))
    tmp = list(filter(lambda s: s != ' ', tmp))
    lineList.extend(tmp)
    return lineList

def GetDuplicateWords(freqDicts):
    Dict = {}
    for key, value in Dict.items():
        if value != 1:
            Dict.update({key: value})
    return Dict

if __name__ == '__main__':

    lines = FilestoLines(sys.argv[1])
    print (len(lines))
#    words = ExtractNoun_en(sys.argv[1])


