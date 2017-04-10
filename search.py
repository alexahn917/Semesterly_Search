import sys
import re
import os
import subprocess
import math
import numpy as np
import pdb
import json
from bs4 import BeautifulSoup
import requests
from PorterStemmer import PorterStemmer
from collections import defaultdict

doc_simula = []
res_vector = []
courses = None
course_vector = None
titles_vector = None
course_code2num = None
course_num2code = None
docs_freq_hash = None
corp_freq_hash = None
stoplist_hash = None
synonyms = None
synonyms_list = None
p = None

def main():
    global courses
    global course_vector
    global titles_vector
    global course_code2num
    global course_num2code
    global docs_freq_hash
    global corp_freq_hash
    
    initialize()
    courses = read_json("json_files/preprocessed_courses.json")
    course_vector = read_json("json_files/course_vector.json")
    titles_vector = read_json("json_files/titles_vector.json")
    course_code2num = read_json("json_files/course_code2num.json")
    course_num2code = read_json("json_files/course_num2code.json")
    docs_freq_hash = read_json("json_files/docs_freq_hash.json")
    corp_freq_hash = read_json("json_files/corp_freq_hash.json")
    total_docs = len(course_vector)

    menu = \
    "============================================================\n"\
    "==      Welcome to the Semester.ly's Search Engine          \n"\
    "==                                                          \n"\
    "==      Total Number of Courses: {0}                        \n"\
    "============================================================\n"\
    "                                                            \n"\
    "OPTIONS:                                                    \n"\
    "  1 = Search for courses using a query                      \n"\
    "  2 = Find most similar courses                             \n"\
    "  3 = Print course vector model                             \n"\
    "  4 = Print course information                              \n"\
    "  5 = Quit                                                  \n"\
    "                                                            \n"\
    "============================================================\n".format(total_docs)

    while True:
        sys.stderr.write(menu)
        option = raw_input("Enter Option: ")
        if option == "1":
            search()
        elif option == "2":
            find_similar_courses()
        elif option == "3":
            code = raw_input("Enter Code: ")
            print_course_vect(code.lower())
        elif option == "4":
            code = raw_input("Enter Code: ")
            print_course_info(code.upper())
        elif option == "5":
            exit(0)
        else:
            sys.stderr.write("Invalid input, please try again\n")


def initialize():
    global p
    global stoplist_hash
    p = PorterStemmer()
    stoplist_hash = set()
    for line in open("txt_files/common_words.stemmed", 'r'):
        if line:
            stoplist_hash.add(line.strip())
    useSynonyms()


def useSynonyms():
    # Using Thesures(Synonyms)
    global synonyms
    global synonyms_list
    synonyms = {}
    synonyms_list = []
    useThesures = True
    if useThesures:
        p = PorterStemmer()
        with open("txt_files/synonyms_short.txt", 'r') as f:
            lines = f.read().split('$')
            index = 0
            for line in lines:
                words_list = []
                words = line.split(',')
                for word in words:
                    word = word.strip()
                    if re.search('[a-zA-Z]', word):
                        word = word.lower()
                        word = p.stem(word, 0, len(word)-1)
                        words_list.append(word)
                        synonyms[word] = index
                synonyms_list.append(words_list)
                index+=1

def find_similar_courses():
    #sys.stderr.write("Retrieving most similar courses to the selected one\n")
    comp_type = raw_input("Type Course Code (XX.###.###): ")
    try:
        int_vector = course_vector[course_code2num[comp_type.lower()]]
    except:
        print("\n*Invalid course code*\n")
        return
    max_show = 15 #int(raw_input("Show how many matching documents (e.g. 20): "))    
    get_retrieved_set(int_vector)
    shw_retrieved_set(max_show, 0, int_vector, "Interactive Query")        


def search():
    max_show = 15 #int(raw_input("Show how many matching documents (e.g. 20): "))
    int_vector = convert_keyboard_query()
    if not int_vector:
        print("\n*Invalid search (no results)*\n")
        return
    get_retrieved_set(int_vector)
    shw_retrieved_set(max_show, 0, int_vector, "Interactive Query")


def convert_keyboard_query():
    qry = raw_input("Search Semeter.ly : ")
    words = qry.strip().split(' ')
    QUERY_WEIGHT = 1
    new_doc_vec = defaultdict(int)
    prev = ""
    for word in words:
        word = word.strip()
        word = word.lower()
        word = p.stem(word, 0, len(word)-1)
        if word in new_doc_vec:
            new_doc_vec[word] += QUERY_WEIGHT
        elif word not in stoplist_hash:
            new_doc_vec[word] = QUERY_WEIGHT
        else:
            continue

        if prev:
            bigram = prev + " " + word
            if bigram in new_doc_vec:
                new_doc_vec[bigram] += QUERY_WEIGHT
            elif bigram in corp_freq_hash:
                new_doc_vec[bigram] = QUERY_WEIGHT
            else:
                continue
        prev = word
    return add_synonyms(new_doc_vec)


def add_synonyms(qry_vect):
    new_vect = defaultdict(int)
    for key in qry_vect:
        if key in corp_freq_hash:
            new_vect[key] = qry_vect[key]
        if key in synonyms:
            sim_words_list = synonyms_list[synonyms[key]]
            for sim_word in sim_words_list:
                if sim_word not in stoplist_hash and re.search("[a-zA-z]", sim_word):
                    if sim_word in corp_freq_hash:
                        new_vect[sim_word] = qry_vect[key]
    return new_vect

###########################################################
## GET_RETRIEVED_SET
##
##  Parameters:
##
##  my_qry_vector    - the query vector to be compared with the
##                  document set. May also be another document
##                  vector.
##
##  This function computes the document similarity between the
##  given vector "my_qry_vector" and all vectors in the document
##  collection storing these values in the array "doc_simula"
##
##  An array of the document numbers is then sorted by this
##  similarity function, forming the rank order of documents
##  for use in the retrieval set.
##
##  The similarity will be
##  sorted in descending order.
##########################################################
def get_retrieved_set(my_qry_vector):
    # "global" variable might not be a good choice in python, but this
    # makes us consistant with original perl script
    global doc_simula, res_vector
    
    tot_number = len(course_vector)

    doc_simula = []   # insure that storage vectors are empty before we
    res_vector = []   # calculate vector similarities

    for index in range(tot_number):
        doc_simula.append(cosine_sim(my_qry_vector, course_vector[index]))

    res_vector = sorted(range(tot_number), key = lambda x: -doc_simula[x])

############################################################
## SHW_RETRIEVED_SET
##
## Assumes the following global data structures have been
## initialized, based on the results of "get_retrieved_set".
##
## 1) res_vector - contains the document numbers sorted in
##                  rank order
## 2) doc_simula - The similarity measure for each document,
##                  computed by &get_retrieved_set.
##
## Also assumes that the following have been initialized in
## advance:
##
##       titles[ doc_num ]    - the document title for a
##                                document number, $doc_num
##       relevance_hash[ qry_num ][ doc_num ]
##                              - is doc_num relevant given
##                                query number, qry_num
##
## Parameters:
##   max_show   - the maximum number of matched documents
##                 to display.
##   qry_num    - the vector number of the query
##   qry_vect   - the query vector (passed by reference)
##   comparison - "Query" or "Document" (type of vector
##                 being compared to)
##
## In the case of "Query"-based retrieval, the relevance
## judgements for the returned set are displayed. This is
## ignored when doing document-to-document comparisons, as
## there are nor relevance judgements.
##
############################################################
def shw_retrieved_set(max_show, qry_num, my_qry_vector, comparison):
    menu = "   ************************************************************\n"\
           "                        Most Similar Courses                   \n"\
           "   ************************************************************\n"\
           "   Similarity   Course No.   Title                             \n"\
           "   ==========   ==========   ==================================\n".format(comparison, qry_num)

    sys.stderr.write(menu)
    num_printed = 0
    
    for index in range(max_show + 1):
        ind = res_vector[index]
        if comparison == "Query" and relevance_hash[qry_num][ind]:
            sys.stderr.write("* ")
        else:
            sys.stderr.write("  ")

        similarity = doc_simula[ind]
        title = titles_vector[ind][:47]
        code = course_num2code[ind]
        if similarity > 0.01:
            sys.stderr.write(" {0:10.8f}   {1}   {2}\n".format(similarity, code.upper(), title))
            num_printed += 1

    if num_printed == 0:
        print("\n\nNo results found.")
        return

    show_terms = raw_input("\nShow the terms that overlap between the query and "\
        "retrieved docs (y/n): ").strip()
    
    if show_terms != 'n' and show_terms != 'N':
        for index in range(max_show + 1):
            ind = res_vector[index]
            show_overlap(my_qry_vector, course_vector[ind], qry_num, ind)
            if (index % 5 == 4):
                cont = raw_input("\nContinue (y/n)?: ").strip()
                if cont == 'n' or cont == 'N':
                    break

########################################################
## SHOW_OVERLAP
##
## Parameters:
##  - Two vectors (qry_vect and doc_vect), passed by
##    reference.
##  - The number of the vectors for display purposes
##
## PARTIALLY IMPLEMENTED:
##
## This function should show the terms that two vectors
## have in common, the relative weights of these terms
## in the two vectors, and any additional useful information
## such as the document frequency of the terms, etc.
##
## Useful for understanding the reason why documents
## are judged as relevant.
##
## Present in a sorted order most informative to the user.
##
########################################################
def show_overlap(my_qry_vector, my_course_vector, qry_num, doc_num):
    info = "============================================================\n"\
           "{0:15s}  {1:8d}   {2:8d}\t{3}\n"\
           "============================================================\n".format(
            "Vector Overlap", qry_num, doc_num, "Docfreq")
    sys.stderr.write(info)
    for term_one, weight_one in my_qry_vector.items():
        if my_course_vector.get(term_one, 0):
            info =  "{0:15s}  {1:f}   {2:8f}\t{3}\n".format(
                term_one, weight_one, my_course_vector[term_one], corp_freq_hash[term_one])
            sys.stderr.write(info)


########################################################
## COSINE_SIM
##
## Computes the cosine similarity for two vectors
## represented as associate arrays. You can also pass the
## norm as parameter
##
## Note: You may do it in a much efficient way like
## precomputing norms ahead or using packages like
## "numpy", below provide naive implementation of that
########################################################
def cosine_sim(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
    if not vec1_norm:
        vec1_norm = sum(v * v for v in vec1.values())
    if not vec2_norm:
        vec2_norm = sum(v * v for v in vec2.values())
    
    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1

    # calculate the cross product
    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
    try:
        return cross_product / math.sqrt(vec1_norm * vec2_norm)
    except:
        return 0

def print_course_vect(course_code):
    try:
        print(course_vector[course_code2num[course_code]])
    except:
        print("\n*Invalid course number*\n")

def print_course_info(course_code):
    try:
        print(course_code)
        course = courses[course_code]
        print "\n=========================================="
        print "TITLE: %s\n" %course['title']
        print "ID: %s\n"%course['ID']
        print "CODE: %s\n"%course['code']
        print "DESCRIPTION: %s\n" %course['description']
        print "INSTRUCTORS: %s\n" %course['instructors']
        print "TERM: %s\n" %course['term']
        print "YEAR: %s\n" %course['year']
    except:
        print("\n*Invalid course number*\n")

def read_json(file_name):
    json_object = open(file_name).read()
    json_object = json_loads_byteified(json_object)
    return json_object

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    return data

if __name__ == '__main__':
    main()



