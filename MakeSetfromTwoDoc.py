#! /usr/bin/env python
#coding:utf-8

wn_path = "wnjpn.db"

import sys
import os
import codecs

from collections import Counter
from ExtractWord import GetWords,FilestoLines
from operator import add
from functools import reduce
from filters import filter_wordsize
from filters import filter_wordnet
#from filters import filter_wiki



def print_std_f(str,file):
    print str
    print >> file, str.encode("utf-8")
    
def write_list(list,file):
    for elem in list:
        print >> file, elem+",",
    print  >> file,"\n"
    
def getfilelist(path):
    file_list = []
    for (root, dirs, files) in os.walk(path):
        for file in files:
            file_list.append( os.path.join(root,file) )
    return file_list

def guess_charset(data):
    f = lambda d, enc: d.decode(enc) and enc

    try: return f(data, 'utf-8')
    except: pass
    try: return f(data, 'shift-jis')
    except: pass
    try: return f(data, 'euc-jp')
    except: pass
    try: return f(data, 'iso2022-jp')
    except: pass
    return None

def conv(data,type):
    charset = guess_charset(data)
    u = data.decode(charset)
    return u.encode(type),charset

def convfile(filepath,type):
    f_in = file(filepath,'r')
    data = f_in.read()
    f_in.close()
    try:
        data, origin_charset = conv(data,type)
    except:
        print filepath + "...convert failed <"+type+">"
        return False

    f_out = file(filepath,'w')
    f_out.write(data)
    f_out.close()
    print filepath + "...converted <"+type+">"
    return origin_charset

def SearchSentenceswithKeyword(lines,docs,keyword):   
    indexList =[]
    searchedlineList=[]
    lineList=[]

    for w in docs:
        if keyword in w:
            i = docs.index(w)
            indexList.append(i)
            searchedlineList.append(w)          
    #for i,s in enumerate(searchedlineList):
    #    print(('ID=',i,':',s,))

    return indexList

def GetWordsfromfile(filepath):
    f = open(filepath)
    words = f.readlines()
    words = [w.replace("\n","") for w in words]
    f.close()
    return words

def GetWordlistfromfile(filepath):
    f = open(filepath)
    words = f.readlines()
    words = [w.replace("\n","") for w in words]
    wordlist = [w.split(" ") for w in words]
    wordlist = [wl[:-1] if len(wl)>1 else wl for wl in wordlist ]
    f.close()
    return wordlist

def MakeSetfromTwoDoc():

    result = ''
    switch = '0'

    filelist = getfilelist('input')
    if len(filelist) == 2:
        path1 = filelist[0]
        path2 = filelist[1]
    else:
        print ("ERROR: Please put ONLY 2 files.")
        raw_input()
        return
    
    ori_charset1 = convfile(path1,type='utf-8')
    ori_charset2 = convfile(path2,type='utf-8')


    df = open('output/result_detail.txt', 'w')
    cf = open('output/words_list.csv', 'w')
    gf = open('output/garbage_words.txt', 'w')

    #df = codecs.open('output/result_detail.txt', 'w','shift-jis')
    #cf = codecs.open('output/words_count.csv', 'w','shift-jis')
    #gf = codecs.open('output/garbage_words.txt', 'w','shift-jis')
    
    if os.sep in path1:
        filename1 = path1.rsplit(os.sep,1)[1]
    else:
        filename1 = path1
    if os.sep in path2:
        filename2 = path2.rsplit(os.sep,1)[1]
    else:
        filename2 = path2

    keylines_filename1 = 'output/keylines_'+filename1+".txt"
    keylines_filename2 = 'output/keylines_'+filename2+".txt"

    lf1 = open(keylines_filename1, 'w')
    lf2 = open(keylines_filename2, 'w')

    try:
        lines1,lang1 = FilestoLines(path1, langoption='en')
        lines2,lang2 = FilestoLines(path2, langoption='en')
    except KeyError:
        print "\nError: These files are written in different language.\n"        
        convfile(path1,type=ori_charset1)
        convfile(path2,type=ori_charset2)
        print "Please press enter key to exit ..."
        raw_input()
        return

    print_std_f("\n===============", file=df)
    print_std_f( "Number of Lines", file=df)
    print_std_f("===============\n", file=df)
    print_std_f( str(len(lines1)) + "\t| "+ filename1, file=df)
    print_std_f( str(len(lines2)) + "\t| "+ filename2, file=df)


    templist = getfilelist('temp')
    if len(templist) == 2:
        raw_words1 = GetWordlistfromfile("temp/temp_rawwords1.txt")
        raw_words2 = GetWordlistfromfile("temp/temp_rawwords2.txt")
    else:
        raw_words1 = GetWords(lines1,"NOUN",langtype=lang1)
        raw_words2 = GetWords(lines2,"NOUN",langtype=lang2)
        
        sf1 = open('temp/temp_rawwords1.txt', 'w')
        sf2 = open('temp/temp_rawwords2.txt', 'w')
        for fw1 in raw_words1:
            for w in fw1:
                print >> sf1, w,
            print >> sf1, ""
        for fw2 in raw_words2:
            for w in fw2:
                print >> sf2, w,
            print >> sf2, ""
        sf1.close()
        sf2.close()


    flatwords1 = reduce(add,raw_words1)
    flatwords2 = reduce(add,raw_words2)        

    set1 = set(flatwords1)
    set2 = set(flatwords2)
    
    print >> df, "\n==============="
    print >> df, "Words (Raw)"
    print >> df, "===============\n"
    
    print >> df, filename1
    write_list(set1, df)
    
    print >> df, filename2
    write_list(set2, df)
    
    print_std_f( "\n==================", file=df)
    print_std_f( "Word Count (Raw)", file=df)
    print_std_f( "===================\n", file=df)
    print_std_f( str(len(flatwords1)) + "\t| "+ filename1 , file=df)
    print_std_f( str(len(flatwords2)) + "\t| "+ filename2 , file=df)
    
    print_std_f( "\n==================", file=df)
    print_std_f( "Vocaburary Size (Raw)", file=df)
    print_std_f( "===================\n", file=df)
    print_std_f( str(len(set1)) + "\t| "+ filename1, file=df)
    print_std_f( str(len(set2)) + "\t| "+ filename2 + "\n", file=df)


    print "\n Now Filtering...\n"
    print >> df, "\n-----------------------\n"
    
    filteredwords1 = [w for w in flatwords1 if filter_wordsize(w,2)==True]
    garbagewords1 = [w for w in flatwords1 if filter_wordsize(w,2)==False]
    filteredwords2 = [w for w in flatwords2 if filter_wordsize(w,2)==True]
    garbagewords2 = [w for w in flatwords2 if filter_wordsize(w,2)==False]
    
    flatwords1 = filteredwords1
    flatwords2 = filteredwords2


    print >> gf, "\n=================="
    print >> gf, "filter_wordsize"
    print >> gf, "===================\n"
    print >> gf, filename1
    write_list(set(garbagewords1), gf)
    print >> gf, filename2
    write_list(set(garbagewords2), gf)
    
    """
    
    keywords = GetWordsfromfile("filter/srs12_6.txt")

    filteredwords1 = [w for w in flatwords1 if w not in keywords]
    garbagewords1 = [w for w in flatwords1 if w in keywords]
    filteredwords2 = [w for w in flatwords2 if w not in keywords]
    garbagewords2 = [w for w in flatwords2 if w in keywords]
    
    flatwords1 = filteredwords1
    flatwords2 = filteredwords2

    print_std_f( "\n==================", file=gf)
    print_std_f( "filter_keyword", file=gf)
    print_std_f( "===================\n", file=gf)
    
    print >> gf,  "filter_keywords: "
    print >> gf,  keywords
    print >> gf,  "\n"
    
    print >> gf, filename1
    write_list(set(garbagewords1), gf)
    print >> gf, filename2
    write_list(set(garbagewords2), gf)
        
    

    filteredwords1 = [w for w in flatwords1 if filter_wiki(w)==True]
    garbagewords1 = [w for w in flatwords1 if filter_wiki(w)==False]
    filteredwords2 = [w for w in flatwords2 if filter_wiki(w)==True]
    garbagewords2 = [w for w in flatwords2 if filter_wiki(w)==False]
    
    flatwords1 = filteredwords1
    flatwords2 = filteredwords2

    print_std_f( "\n==================", file=gf)
    print_std_f( "filter_wiki", file=gf)
    print_std_f( "===================\n", file=gf)
    print >> gf, filename1
    write_list(set(garbagewords1), gf)
    print >> gf, filename2
    write_list(set(garbagewords2), gf)

    """

    filteredwords1 = [w for w in flatwords1 if filter_wordnet(w,sensenum_min=1)==True]
    garbagewords1 = [w for w in flatwords1 if filter_wordnet(w,sensenum_min=1)==False]
    filteredwords2 = [w for w in flatwords2 if filter_wordnet(w,sensenum_min=1)==True]
    garbagewords2 = [w for w in flatwords2 if filter_wordnet(w,sensenum_min=1)==False]
    
    print_std_f( "\n==================", file=gf)
    print_std_f( "filter_wordnet", file=gf)
    print_std_f( "===================\n", file=gf)
    print >> gf, filename1
    write_list(set(garbagewords1), gf)
    print >> gf, filename2
    write_list(set(garbagewords2), gf)
    
    flatwords1 = filteredwords1
    flatwords2 = filteredwords2
    
    

    counter1 = Counter(flatwords1)
    counter2 = Counter(flatwords2)

    set1 = set(flatwords1)
    set2 = set(flatwords2)

    
    print >> df, "\n==============="
    print >> df, "Words (Filtered)"
    print >> df, "===============\n"
    
    print >> df, filename1
    write_list(set1, df)
    
    print >> df, filename2
    write_list(set2, df)
    

    print_std_f( "\n===================", file=df)
    print_std_f( "Word Count (Filtered)", file=df)
    print_std_f( "====================\n", file=df)
    print_std_f( str(len(flatwords1)) + "\t| "+ filename1 , file=df)
    print_std_f( str(len(flatwords2)) + "\t| "+ filename2 , file=df)
    
    
    print_std_f( "\n========================", file=df)
    print_std_f( "Vocaburary Size (Filtered)", file=df)
    print_std_f( "=========================\n", file=df) 
    print_std_f( str(len(set1)) + "\t| "+ filename1, file=df)
    print_std_f( str(len(set2)) + "\t| "+ filename2 + "\n", file=df)
    
    
    print_std_f( "\n=====================", file=df)
    print_std_f( "! PLEASE INPUT NUMBER !", file=df)
    print_std_f( "======================\n", file=df)
    print_std_f( '1: ' + filename1 + u' ― ' + filename2 + "(set)"+ "\n", file=df)
    print_std_f( '2: ' + filename1 + u' ∩ ' + filename2 + "(set)" + "\n", file=df)
    print_std_f( '3: ' + filename2 + u' ― ' + filename1 + "(set)" + "\n", file=df)
    print_std_f( '4: ' + filename1 + u' ― ' + filename2 + "(count)" + "\n", file=df)
    print_std_f( '5: ' + filename2 + u' ― ' + filename1 + "(count)" + "\n", file=df)
    print_std_f( '6: ' + filename1 + u' ∩ ' + filename2 + "(set) multi-meaning \n", file=df)

    vocab_cnt = 0
    word_cnt = 0
    result_wordlist = []

    while 1:
        switch = raw_input()

        if switch == '1':
            print >> cf, "word"+","+filename1+","+filename2  
            for word,cnt in counter1.most_common():
                sub_cnt = counter2[word]
                if sub_cnt == 0:
                    word_cnt += cnt
                    result_wordlist.append(word)
                    print >> cf, word+","+str(cnt)+","+str(sub_cnt)
            break

        elif switch == '2':
            print >> cf, "word"+","+filename1+","+filename2  
            for word,cnt in counter1.most_common():
                sub_cnt = counter2[word]
                if sub_cnt != 0:
                    word_cnt += cnt
                    result_wordlist.append(word)
                    print >> cf, word+","+str(cnt)+","+str(sub_cnt)
            
            break

        elif switch == '3':
            print >> cf, "word"+","+filename1+","+filename2  
            for word,cnt in counter2.most_common():
                sub_cnt = counter1[word]
                if sub_cnt == 0:
                    word_cnt += cnt
                    result_wordlist.append(word)
                    print >> cf, word+","+str(sub_cnt)+","+str(cnt)
            break

        elif switch == '4':
            print >> cf, "word"+","+filename1+","+filename2+","+filename1+"-"+filename2 
            dif_counter = counter1 - counter2
            for word,dif_cnt in dif_counter.most_common():
                main_cnt = counter1[word]
                sub_cnt = counter2[word]
                word_cnt += dif_cnt
                result_wordlist.append(word)
                print >> cf, word+","+str(main_cnt)+","+str(sub_cnt)+","+str(dif_cnt)
            break

        elif switch == '5':
            print >> cf, "word"+","+filename1+","+filename2+","+filename2+"-"+filename1 
            dif_counter = counter2 - counter1 #実験環境でエラーになる原因？
            for word,dif_cnt in dif_counter.most_common():
                main_cnt = counter1[word]
                sub_cnt = counter2[word]
                word_cnt += dif_cnt
                result_wordlist.append(word)
                print >> cf, word+","+str(main_cnt)+","+str(sub_cnt)+","+str(dif_cnt)
            break

        elif switch == '6':
            if os.path.isfile(wn_path) == False:
                print "\nERROR:"
                print "WORDNET database file is not found."
                print "Please put 'wnjpn.db' on this directory."
                print "You can download from 'http://nlpwww.nict.go.jp/wn-ja/data/1.1/wnjpn.db.gz' ."
                print "Please press enter key to exit ..."
                raw_input()
                return
            else:
                print >> cf, "word"+","+filename1+","+filename2+","+filename2+"-"+filename1 
                for word,cnt in counter1.most_common():
                    sub_cnt = counter2[word]
                    if sub_cnt != 0 and filter_wordnet(word,sensenum_min=2) == True:
                        word_cnt += cnt
                        result_wordlist.append(word)
                        print >> cf, word+","+str(cnt)+","+str(sub_cnt)
                    else:
                        continue
                break

    
    print_std_f( "\nINPUT NUMBER :" + switch, file=df)
    
    
    print >> df, "\n===============" 
    print >> df, "Words (Result)"
    print >> df, "===============\n"

    write_list(result_wordlist,df)


    print_std_f( "\n========================", file=df)
    print_std_f( "Word Count (Result)", file=df)
    print_std_f( "=========================\n", file=df) 
    print_std_f( str(word_cnt) , file=df)
    
    print_std_f( "\n========================", file=df)
    print_std_f( "Vocaburary Size (Result)", file=df)
    print_std_f( "=========================\n", file=df) 
    print_std_f( str(len(result_wordlist)) , file=df)
 

    for w in result_wordlist:
        indexlist1 = SearchSentenceswithKeyword(lines1,raw_words1,w)
        indexlist2 = SearchSentenceswithKeyword(lines2,raw_words2,w)
        
        print >> lf1, "[",w,"]"
        for index in indexlist1:
            print >> lf1, lines1[index]+"<END>"
        print >> lf1, ""
        print >> lf2, "[",w,"]"
        for index in indexlist2:
            print >> lf2, lines2[index]+"<END>"
        print >>lf2, ""


    df.close()
    cf.close()
    gf.close()
    lf1.close()
    lf2.close()
    
    convfile('output/result_detail.txt',type='shift-jis')
    convfile('output/garbage_words.txt',type='shift-jis')
    convfile('output/words_list.csv',type='shift-jis')
    convfile(keylines_filename1,type='shift-jis')
    convfile(keylines_filename2,type='shift-jis')

    convfile(path1,type=ori_charset1)
    convfile(path2,type=ori_charset2)

    print ""
    print "COMPLETED"
    print "Please press enter key to exit ..."
    raw_input()
    return

if __name__ == "__main__":

    MakeSetfromTwoDoc()
