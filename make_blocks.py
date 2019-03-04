# -*- coding: utf-8 -*-

import re
import os
import pickle
import sys
from pymongo import MongoClient

question_pattern  = re.compile(r'^(Întrebarea|Î|intrebarea|Intrebarea|intrebare|I|#)?\s*\d{1,2}\s*(;|\.|-|:|\))?')
answer_pattern    = re.compile(r'^((Ră|ră|Ra|ra)spuns)|(\.S)\s*(\.|:|-|=)')
comment_pattern   = re.compile(r'^((Comentari[ui]|C)(:|-|\.)\s*)')
source_pattern    = re.compile(r'^((S|s)urs(ă|a)|src|Src|S)\s*(:|-)\s*')
author_pattern    = re.compile(r'^A(utor)?:\s')
hyperlink_pattern = re.compile(r'http(s)?://',re.M)


def process_one(f,verbose=False):
    lines = f.readlines()
    for i in range(len(lines)):
        lines[i] = re.sub(r'^\s*','',lines[i])
        if  re.match(question_pattern, lines[i]) or \
            re.match(answer_pattern,   lines[i]) or \
            re.match(comment_pattern,  lines[i]) or \
            re.match(source_pattern,   lines[i]) or \
            re.match(author_pattern,   lines[i]):
            lines[i] = "\n" + lines[i]
    return lines

def process_all():
    for filename  in os.listdir("./unprocessed/txt/"):
        sys.stdout.write('%s:      '% ("{:<30}".format(filename)))

        if not filename.endswith(".txt"):
            continue
        f = open("./unprocessed/txt/%s"%filename,"r")
        result = open("./unprocessed/txt/blocks/%s"%filename,"w")
        lines = process_one(f)
        result.write(''.join(lines))

if __name__ == '__main__':
    f = open("./cupa.txt","r")
    result  = open("./blocks.txt","w")
    lines = process_one(f)
    result.write(''.join(lines))
