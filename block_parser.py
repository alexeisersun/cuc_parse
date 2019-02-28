# -*- coding: utf-8 -*-
import re
import os
import pickle
import sys

question_pattern  = re.compile(r'^((I|Î)ntrebare(a)?)?(:)?(\s)*\d{1,2}(\s)*(;|\.|\-|:|\)?)?',re.I)
answer_pattern    = re.compile(r'^(((Ră|Ra)spuns)|(R\.S|Rsp|R))\s*(\.|:|-|=)',re.I)
comment_pattern   = re.compile(r'^((Comentari[ui]|C)(;|:|-|\.)\s*)', re.I)
source_pattern    = re.compile(r'^(surs(ă|a|e))\s*(:|-)\s*', re.I)
author_pattern    = re.compile(r'^A(utor)?:\s*',re.I)
hyperlink_pattern = re.compile(r'http(s)?://',re.I | re.M)

map_categories = [ 'question', 'answer', 'comment', 'source', 'author', 'unknown' ]

def add_lines_btw_blocks(f,verbose=False):
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

def get_blocks(lines):
    #find empty lines
    empty_indices = []
    for i in range(len(lines)):
        empty_match = re.search(r'^\s+$',lines[i])
        if(empty_match):
            empty_indices.append(i)

    #discount empty line that are surrounded by empty lines
    to_delete = []
    if empty_indices[0] == 0:
        to_delete.append(0)
    for i in range(len(empty_indices)-2,0,-1):
        if empty_indices[i-1] == empty_indices[i] - 1 or empty_indices[i+1] == empty_indices[i] + 1:
            to_delete.append(i)

    for i in to_delete:
        del empty_indices[i]

    #now empty_indices contains the indices of the lines that separate blocks of text
    #print(empty_indices)
    empty_indices.insert(0,-1)
    empty_indices.append(len(lines)-1)
    blocks = []
    for i in range(len(empty_indices)-1):
        blocks.append(''.join([lines[i] for i in range(empty_indices[i]+1,empty_indices[i+1])]))

    for i in range(len(blocks)):
        blocks[i] = re.sub(r'\n',' ',blocks[i])
    return blocks

def categorize_blocks(blocks):
    #categorize each block
    categories = [5 for b in blocks]
    """
    0: question
    1: answer
    2: comment
    3: source
    4: author
    5: unknown
    """

    for i in range(len(blocks)):
        if re.match(question_pattern,blocks[i]):
            categories[i] = 0
            blocks[i] = re.sub(question_pattern,'',blocks[i])
        elif re.match(answer_pattern,blocks[i]):
            categories[i] = 1
            blocks[i] = re.sub(answer_pattern,'',blocks[i])
        elif re.match(comment_pattern,blocks[i]):
            categories[i] = 2
            blocks[i] = re.sub(comment_pattern,'',blocks[i])
        elif re.match(source_pattern,blocks[i]) or re.search(hyperlink_pattern,blocks[i]):
            categories[i] = 3
            blocks[i] = re.sub(source_pattern,'',blocks[i])
        elif re.match(author_pattern,blocks[i]):
            categories[i] = 4
            blocks[i] = re.sub(author_pattern,'',blocks[i])


    for i in range(len(blocks)-2,-1,-1):
        if categories[i] == 5:
            if categories[i+1] == 1 or categories[i+1] == 0:
                categories[i] = 0
    #merge neighboring blocks of the same category 
    i = 0
    while i < len(blocks)-1:
        while(i<len(blocks)-1 and categories[i+1] == categories[i]):
            blocks[i] += '\n' + blocks[i+1]
            del blocks[i+1]
            del categories[i+1]
        i+=1

    i = 0
    while i<len(blocks):
        if categories[i] == 5:
            del blocks[i]
            del categories[i]
        i+=1
    return (blocks,categories)

def empty_question_object():
    return {
        "question":"",
        "answer"  :"",
        "comment" :"",
        "source"  :"",
        "authors" :""
    }

def get_question_objects(blocks,categories):
    question_objects = []
    current_question_object = empty_question_object()
    last_found = 5
    for i in range(len(blocks)):
        if(categories[i] == 0): #question
            if last_found not in [0,5]:
                question_objects.append(current_question_object)
            current_question_object = empty_question_object()
            current_question_object["question"] = blocks[i]
            last_found = 0
        if(categories[i] == 1): #answer
            if last_found == 0:
                current_question_object["answer"] = blocks[i]
                last_found = 1
            else:
                last_found = 5
                current_question_object = empty_question_object()
        if(categories[i] == 2): #comment
            if last_found in [1,4]:
                current_question_object["comment"] = blocks[i]
                last_found = 2
            else:
                last_found = 5
                current_question_object = empty_question_object()
        if(categories[i] == 3): #source
            if last_found in [1,2,4]:
                current_question_object["source"] = blocks[i]
                last_found = 3
            else:
                last_found = 5
                current_question_object = empty_question_object()
        if(categories[i] == 4): #Author
            if last_found in [0,1,2,3]:
                current_question_object["authors"] = blocks[i]
                last_found = 4
            else:
                last_found = 5
                current_question_object = empty_question_object()
    if(last_found != 5):
        question_objects.append(current_question_object)
    return question_objects

def parse_file(filename,verbose=False):
    name = filename.split("/")[-1]
    sys.stdout.write("%s"%("{:<30}".format(name)))
    f                   = open(filename,"r")
    file_with_blocks    = open("./unprocessed/txt/blocky/%s"%name,"w+")
    lines               = add_lines_btw_blocks(f)
    f.close()
    file_with_blocks.write(''.join(lines))
    file_with_blocks.close()
    f                   = open("./unprocessed/txt/blocky/%s"%name,"r")
    info_f              = open("./info/%s"%re.sub(r'.txt$','.info',name),"r")
    info                = pickle.load(info_f)
    num_questions       = int(info["number_of_questions"])
    lines = f.readlines()
    blocks = get_blocks(lines)
    (blocks,categories)= categorize_blocks(blocks)
    if verbose:
        for i in range(len(blocks)):
            print(blocks[i])
            print("CATEGORY:   %s\n\n%s"%(categories[i],"*"*80))
    question_objects = get_question_objects(blocks,categories)
    sys.stdout.write("%d/%d\n"%(len(question_objects),num_questions))
    if verbose:
        for q in question_objects:
            print("QUESTION     : %s\nANSWER       : %s\nCOMMENT      : %s\nSOURCE       : %s\nAUTHOR       : %s\n\n\
                   *********************************************************************\n\n\
                   "%(q["question"], q["answer"], q["comment"], q["source"], q["authors"]))

    return (question_objects,num_questions)

def parse_all():
    total = 0
    successful = 0
    for filename  in os.listdir("./unprocessed/txt/"):
        if not filename.endswith(".txt"):
            continue
        (question_objects,num_questions) = parse_file("./unprocessed/txt/%s"%filename)
        total += num_questions
        successful += len(question_objects)

    print("%d/%d SUCCESSFUL"%(successful ,total))


if __name__ == '__main__':
    arguments = sys.argv
    if(arguments[1] == "all"):
        parse_all()
    else:
        filename = arguments[1]
        if not filename.endswith(".txt"):
            print("Must be a *.txt file!")
        else:
            (question_objects, num_questions) = parse_file(filename,True)
            print("Parsed %d/%d questions!"%(len(question_objects),num_questions))
