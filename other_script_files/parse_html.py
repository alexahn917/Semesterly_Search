from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import re
import requests

cs_course_page = 'http://e-catalog.jhu.edu/departments-program-requirements-and-courses/engineering/computer-science/#courseinventory'

page = requests.get(cs_course_page)

soup = BeautifulSoup(page.content, 'html.parser')

course_title = soup.find_all("p", class_="courseblocktitle")
course_descp = soup.find_all("p", class_="courseblockdesc")

p = PorterStemmer()

TITLE = 2
DESC = 1

full_doc_vect = []

full_doc_vect.append(defaultdict(int))

docs_freq_hash = {}
corp_freq_hash = {}

for i in range(len(course_title)):
    doc_vect = {}
    doc_vect = {}
    
    terms = set()

    title_word_vect = course_title[i].get_text().split(' ')
    descp_word_vect = course_descp[i].get_text().split(' ')

    prev = ""
    for title_word in title_word_vect:
        title_word = title_word.strip().encode('ascii', 'ignore')
        if re.search('\w+', title_word):
            title_word = str(re.search('\w+', title_word).group(0))
            title_word = title_word.lower()
            title_word = p.stem(title_word, 0, len(title_word)-1)
            if title_word not in doc_vect:
                doc_vect[title_word] = TITLE
            else:
                doc_vect[title_word] += TITLE

            if title_word not in corp_freq_hash:
                corp_freq_hash[title_word] = 1
            else:
                corp_freq_hash[title_word] += 1
            
            terms.add(title_word)

            if prev:
                bigram = prev+title_word
                if bigram not in doc_vect:
                    doc_vect[bigram] = TITLE
                else:
                    doc_vect[bigram] += TITLE

                if bigram not in corp_freq_hash:
                    corp_freq_hash[bigram] = 1
                else:
                    corp_freq_hash[bigram] += 1
                term.add(bigram)

    prev = ""
    for descp_word in descp_word_vect:
        descp_word = descp_word.strip().encode('ascii', 'ignore')
        if re.search('\w+', descp_word):
            descp_word = str(re.search('\w+', descp_word).group(0))
            descp_word = descp_word.lower()
            descp_word = p.stem(descp_word, 0, len(descp_word)-1)
            if descp_word not in doc_vect:
                doc_vect[descp_word] = DESC
            else:
                doc_vect[descp_word] += DESC

            if descp_word not in corp_freq_hash:
                corp_freq_hash[descp_word] = 1
            else:
                corp_freq_hash[descp_word] += 1                   
            terms.add(descp_word)

            if prev:
                bigram = prev+descp_word
                if bigram not in doc_vect:
                    doc_vect[bigram] = DESC
                else:
                    doc_vect[bigram] += DESC

                if bigram not in corp_freq_hash:
                    corp_freq_hash[bigram] = 1
                else:
                    corp_freq_hash[bigram] += 1
                term.add(bigram)

    for term in terms:
        if term not in docs_freq_hash:
            docs_freq_hash[term] = 1
        else:
            docs_freq_hash[term] += 1

    full_doc_vect.append(doc_vect)
    

