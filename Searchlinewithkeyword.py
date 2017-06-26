#! /usr/bin/env python
#coding:utf-8


from wn import getSenseNum
import urllib
#import urllib.request
import sys



def get_wikihtml(word):
    url = "http://ja.wikipedia.org/wiki/" + quote(word)
    print (url)
    response = urllib.request.urlopen(url)
    data = response.read()
    decoded_data = data.decode("utf8")
    return decoded_data

def filter_wiki_ambiguous(word): 
    try:
        html = get_wikihtml(word)
    except:
        html = "NONE"
    #keys = ["(曖昧さ回避)</a>","曖昧さ回避のためのページ","における"+word+"</span>"]
    keys = ["(曖昧さ回避)</a>","曖昧さ回避のためのページ"]
    if any([key in html for key in keys]):
        print((word,":AMBIGUOUS"))
        return True
    else:
        print((word,":only"))
        return False

def filter_wiki(word):
    #word = word.decode("utf-8")
    url = "http://ja.wikipedia.org/wiki/" + urllib.quote(word)
    print url
    try:
        f = urllib.urlopen(url)
        f.close()
    except:
        return False
    return True
        
def get_wn_en(word):
    url = "http://wordnetweb.princeton.edu/perl/webwn?s=" + quote(word) + "&sub=Search+WordNet&o2=&o0=1&o8=1&o1=1&o7=&o5=&o9=&o6=&o3=&o4=&h="
    print (url)
    response = urllib.request.urlopen(url)
    data = response.read()
    decoded_data = data.decode("utf8")
    return decoded_data

    
def filter_wn_en(word): 
    try:
        html = get_wn_en(word)
    except:
        html = "NONE"
        return False
    
    keyphrase = "<b>"+word+"</b>"
    counter = html.count(keyphrase)
    if counter >= 2:
#        print((word,":AMBIGUOUS"))
        return True
    else:
        print((word,":only"))
        return False
    
def filter_wordnet(word,sensenum_min):
    sensenum = getSenseNum(word)
    if sensenum >= sensenum_min:
        return True
    else:
        return False

def filter_wordsize(word,size_lim):
    word = word.decode("utf-8")
    if len(word) >= size_lim:
        return True
    else:
        return False
        

def filter_JapaneseDict(Word):
    dic_path = '/media/iso'
    eblook_command = 'eblook ' + dic_path
    select_command = 'select 1\n'
    search_command = 'search ' + Word + '\n'
    result = ''

    p = subprocess.Popen(
        eblook_command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    lines = p.communicate(bytes(select_command + search_command, 'utf-8'))
    result = lines[0].decode('utf-8')
#    print  ((Word) + str(Word in lines[0]))
    if result != "":
        return True
    else:
    	return False
