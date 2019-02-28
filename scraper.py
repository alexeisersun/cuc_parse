"""
This script downloads all the quesiton packages from http://www.cuc.md/content/blogcategory/163/187
and puts them in ./download/
In addition to that, it scrapes information from the table on that page, creates a dictionary containing that info
and dumps it into ./info/<filename>.info (using pickle)
"""

from bs4 import BeautifulSoup
import re
import urllib2
import pickle
import sys

def progress(iteration, total, prefix ='', suffix = '', decimals = 1, length = 50, fill = '='):
    """
    Call in a loop to create terminal progress bar
    @params:
    iteration   - Required  : current iteration (Int)
    total       - Required  : total iterations (Int)
    prefix      - Optional  : prefix string (Str)
    suffix      - Optional  : suffix string (Str)
    decimals    - Optional  : positive number of decimals in percent complete (Int)
    length      - Optional  : character length of bar (Int)
    fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print "\r%s |%s| %s%% %s"%(prefix, bar, percent, suffix),'\r',
    # Print New Line on Complete
    if iteration == total:
        print()

#get page
base_url = 'http://www.cuc.md/'
webpage = urllib2.urlopen('http://www.cuc.md/content/blogcategory/163/187/lang,ro/')
html = webpage.read()
soup = BeautifulSoup(html, 'html.parser')

#find all tr
question_info = { 'competition' : ''}

total = 0
for tr in soup.find_all('tr'):
    cells = tr.find_all('td')
    num_cells = len(cells)
    if num_cells!=7 and num_cells!=8:
        continue
    total+=1

count = 0
for tr in soup.find_all('tr'):
    question_info['stage']               = ""
    question_info['date']                = ""
    question_info['authors']             = ""
    question_info['editor']              = ""
    question_info['number_of_questions'] = ""
    question_info['level']               = ""

    cells = tr.find_all('td')
    num_cells = len(cells)

    if num_cells!=7 and num_cells!=8:
        #we only care about rows that have 7 or 8 cells
        continue

    link = None

    try:
        #get link from last cell if there is one
        link = cells[-1].find_all('a')[0].get('href')
    except:
        #if not, go to next row
        continue

    filename_pattern = re.compile(r'(?P<filename>\w+)\.(?P<extension>pdf|doc|docx)')

    file_match = re.search(filename_pattern,link)
    if not file_match:
        continue

    filename  = file_match.group("filename")
    extension = file_match.group("extension")

    progress(count,total,suffix=filename+"."+extension)

    j=0
    if num_cells == 8:
        #this row contains the name of the competition (spans multiple rows)
        question_info['competition'] = str(cells[j].get_text().encode("utf-8"))
        j+=1

    if cells[j].string:
        question_info['stage']               = str( cells[j].string.encode("utf-8") )
    if cells[j+1].string:
        question_info['date']                = str( cells[j+1].string.encode("utf-8") )
    if cells[j+2].string:
        question_info['authors']             = str( cells[j+2].string.encode("utf-8") )
    if cells[j+3].string:
        question_info['editor']              = str( cells[j+3].string.encode("utf-8") )
    if cells[j+4].get_text():
        question_info['number_of_questions'] = str( cells[j+4].get_text().encode("utf-8") )
    if cells[j+5].string:
        question_info['level']               = str( cells[j+5].string.encode("utf-8") )


    #sanitize
    for e in question_info.keys():
        if question_info[e] is not None:
            question_info[e] = re.sub(r'(\xc2\xa0|\xc2|\xa0|\n)','',question_info[e])
        else:
            question_info[e] = ""

    full_link = base_url + link

    try:
        filedata = urllib2.urlopen(full_link.encode("utf-8"))
        datatowrite = filedata.read()
        with open('./download/%s.%s'%(filename,extension), 'wb') as f:
            f.write(datatowrite)
            count+=1
        with open('./info/%s.info'%filename,'wb') as f:
            pickle.dump(question_info,f)
    except:
        pass



