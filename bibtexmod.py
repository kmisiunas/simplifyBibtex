#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 17:39:41 2018

@author: Karolis Misiunas
"""

import bibtexparser as bt



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


path = '/Users/kmisiunas/Documents/Tools/Mendeley/library.bib'
outpath = '/Users/kmisiunas/Documents/Tools/Mendeley/librarySimple.bib'

bibfile = open(path)

bdb = bt.load(bibfile)

keeplist = ['ENTRYTYPE', 'ID', 'author', 'doi', 'journal', 'number', 'pages', 'title', 'volume', 'year']
bdi = bdb.entries_dict

bibfile.close()

outdict = {}

for entrykey in bdi.keys():
    entry = bdi[entrykey]
    entrykeeplist = [key for key in entry.keys() if key in keeplist]
    newentry = {key: entry[key] for key in entrykeeplist}
    outdict[entrykey] = newentry

lines = []
for (key, entry) in outdict.items():
    lines += createEntryStr(entry)


with open(outpath, 'w') as outfile:
    outfile.writelines(lines)
