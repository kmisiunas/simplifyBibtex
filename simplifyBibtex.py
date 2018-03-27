#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplify Bibtex files
===

Takes one file and simplifies it to have only the relevant citations and relevant fields 

@author: Karolis Misiunas
"""

import bibtexparser as bt
import sys, os
import re
import numpy as np



### Inputs 

if len(sys.argv) <= 1:
    "simplifyBibtex usage: simplifyBibtex.py document.tex [library_out.bib]"
else:
    in_file = sys.argv[1]
    if len(sys.argv) >= 3: 
        out_file = sys.argv[2] 
    else:
        out_file =  "bib_library.bib"

print("simplifyBibtex:", in_file)

### Find bib library 


bib_library_file = ""

for line in open(in_file, "r"):

    if re.match("\\\\bibliography", line):
        bib_library_file = line[line.find("{")+1 : line.find("}")] + ".bib"

if bib_library_file == "":
    print("Error: bibliography library not found. quitting")
    exit()
else:
    print("bibliography library at:",bib_library_file)



### Find all the citation keys in the doc


keys = []

def stringToCitationList(s):
    "deal with cite keys and multiple citations"
    return s.split(",")

for line in open(in_file, "r"):
    for cite in re.findall("\\\\cite{(.*?)}", line):
        #print(cite)
        keys = keys + stringToCitationList(cite)

keys = np.unique(keys)

print("found", len(keys), "unique citations. Eg: ",keys[0])



### Load all citations 


with open(bib_library_file, 'r') as file:
    libraryDB = bt.load(file)
    library = libraryDB.entries_dict


print("library has", len(library.keys()), "citations.")



### Find citations and simplify them 




def simplify(cite):
    """
    Simplifies citation entry
    This simply passes the citation to different simplification engine and returns the first on that does not return false.
    sub-methods should return false if they can parse this 
    """
    #print("[",cite["ID"],"]: ", cite.keys()) # debug
    x = simplifyArxiv(cite)
    if x != False: return x
    x = simplifyArticle(cite)
    if x != False: return x
    x = simplifyBook(cite)
    if x != False: return x
    x = simplifyMisc(cite)
    if x != False: return x
    x = simplifyBookChapter(cite)
    if x != False: return x
    x = simplifyUniversal(cite)
    if x != False: return x


def simplifyArxiv(cite):
    "for arxiv"
    if 'journal' in cite and cite['journal'].lower() == 'arxiv':
        #print("found arxiv entry: ", cite['ID'])
        cite =  filterByKeys(cite, ['author',  'arxivid', 'title',  'year', 'archiveprefix'], [])
        cite['journal'] = cite['archiveprefix'] + ":" + cite['arxivid']
        cite.pop('arxivid', None)
        cite.pop('archiveprefix', None)
        return cite
    else:
        return False

def simplifyArticle(cite):
    if cite['ENTRYTYPE'].lower() == 'article':
        return filterByKeys(cite, ['author', 'title', 'journal', 'number', 'pages',  'year', 'volume'],[])
    else:
        return False

def simplifyBook(cite):
    if cite['ENTRYTYPE'].lower() == 'book':
        return filterByKeys(cite, ['author', 'title', 'publisher',  'year'],[]) #'city',
    else:
        return False

def simplifyMisc(cite):
    if cite['ENTRYTYPE'].lower() == 'misc':
        print("[",cite["ID"],"] is MISC item - manual inspection recommended")
        return filterByKeys(cite, [],['author', 'title', 'url',  'year']) #'city',
    else:
        return False

def simplifyBookChapter(cite):
    if cite['ENTRYTYPE'].lower() == 'incollection':
        print("[",cite["ID"],"] is incollection item - manual inspection recommended")
        cite2 = filterByKeys(cite, ['author' , 'year', 'pages', 'publisher' ],[]) #'city',
        cite2['chapter'] = cite['title']
        cite2['title'] = cite['booktitle']
        return cite2
    else:
        return False

def simplifyUniversal(cite):
    "for anything really"
    return filterByKeys(cite, [], ['author', 'doi', 'journal', 'number', 'pages', 'title', 'volume', 'year'])


def filterByKeys(cite, keys_must, keys_nice):
    "filters the citation. checks to have keys_must and included keys_must and keys_nice"
    # check for having all
    missing_keys = set(keys_must) - set(cite.keys())  
    if len(missing_keys)>0:
        print("[",cite["ID"],"] is missing properties:", missing_keys)
    # filter
    keeplist = ['ENTRYTYPE', 'ID',] + keys_must + keys_nice
    entrykeeplist = [key for key in cite.keys() if key in keeplist]
    newentry = {key: cite[key] for key in entrykeeplist}
    return newentry





citations = {key: simplify(library[key]) for key in keys} 





### Out we go! save the work


def createEntryStr(entry):
    lines = []
    s = '@'
    s += entry['ENTRYTYPE'] + '{' + entry['ID'] + ',\n'
    lines.append(s)
    restkeys = [key for key in entry.keys() if key not in ['ENTRYTYPE', 'ID']]
    for key in restkeys:
        s = ''
        s += key + ' = {'
        s += entry[key] + '},\n'
        lines.append(s)
    lines.append('}\n')
    return lines


lines = []
for (key, entry) in citations.items():
    lines += createEntryStr(entry)


with open(out_file, 'w') as outfile:
    outfile.writelines(lines)

print("saved simple library in:", out_file, " done.")

### Fin
