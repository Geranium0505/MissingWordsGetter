#! /usr/bin/env python
#coding:utf-8

import sys
import os
import codecs

from collections import Counter
from ExtractWord import GetWords,FilestoLines
from operator import add
from functools import reduce



def GetWordsfromfile(filepath):
    f = open(filepath)
    words = f.readlines()
    words = [w.replace("\n","") for w in words]
    f.close()
    return words


def minidiff():
    words1 = GetWordsfromfile("input/dif_no_filter.txt")
    words2 = GetWordsfromfile("input/dif_filter2_12.txt")
    dif = list (set(words1) - set(words2) )
    print dif 
    return

if __name__ == "__main__":

    minidiff()
