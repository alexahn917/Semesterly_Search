import pickle
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

COURSE_VECTOR = None
CODE_2_ID = None
ID_2_CODE = None

docs_freq_hash = None
corp_freq_hash = None
stoplist_hash = None

synonyms = None
synonyms_list = None

p = None
N = None

TITLES = None

def read_files():
    global N
    global courses
    global COURSE_VECTOR
    global COURSE_VECTOR_NORMS
    global CODE_2_ID
    global ID_2_CODE
    global docs_freq_hash
    global corp_freq_hash
    global TITLES
    
    courses = read_json("../json_files/preprocessed_courses_fa2017.json")
    COURSE_VECTOR = read_json("../json_files/COURSE_VECTOR.json")
    COURSE_VECTOR_NORMS = read_json("../json_files/COURSE_VECTOR_NORMS.json")    
    TITLES = read_json("../json_files/TITLES.json")
    CODE_2_ID = read_json("../json_files/CODE_2_ID.json")
    ID_2_CODE = read_json("../json_files/ID_2_CODE.json")
    docs_freq_hash = read_json("../json_files/docs_freq_hash.json")
    corp_freq_hash = read_json("../json_files/corp_freq_hash.json")
    N = len(COURSE_VECTOR)


def main():
    read_files()
    initialize()

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
    "============================================================\n".format(N)

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
    for line in open("../txt_files/common_words.stemmed", 'r'):
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
        with open("../txt_files/synonyms_short.txt", 'r') as f:
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


def search():
    max_show = 15 #int(raw_input("Show how many matching documents (e.g. 20): "))
    qry, qry_vect = convert_keyboard_query()
    if not qry_vect:
        print("\n*Invalid search (no results)*\n")
        return
    get_retrieved_set(qry, qry_vect)
    shw_retrieved_set(max_show, qry_vect)


def convert_keyboard_query():
    qry = raw_input("Search Semeter.ly : ").lower()
    words = qry.strip().split(' ')
    QUERY_WEIGHT = 1
    new_doc_vec = defaultdict(int)
    prev = ""
    for word in words:
        word = word.strip()
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
    return (qry, add_synonyms(new_doc_vec))


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


def find_similar_courses():
    #sys.stderr.write("Retrieving most similar courses to the selected one\n")
    comp_type = raw_input("Type Course Code (XX.###.###): ")
    try:
        course_vect = COURSE_VECTOR[CODE_2_ID[comp_type.lower()]]
    except:
        print("\n*Invalid course code*\n")
        return
    max_show = 15 #int(raw_input("Show how many matching documents (e.g. 20): "))    
    get_retrieved_set(None, course_vect)
    shw_retrieved_set(max_show, course_vect)        



def get_retrieved_set(qry, my_qry_vector):
    global doc_simula, res_vector
    N = len(COURSE_VECTOR)
    doc_simula = []   # insure that storage vectors are empty before we
    res_vector = []   # calculate vector similarities
    for index in range(N):
        score = cosine_sim(my_qry_vector, COURSE_VECTOR[index], 0.0, COURSE_VECTOR_NORMS[index])
        if qry:
            count = 0
            for q in qry.split():
                if q in TITLES[index].lower():
                    count+=1
            if count == len(qry.split()):
                score+=1
        doc_simula.append(score)
    res_vector = sorted(range(N), key = lambda x: -doc_simula[x])


def shw_retrieved_set(max_show, my_qry_vector):
    menu = "   ************************************************************\n"\
           "                        Most Similar Courses                   \n"\
           "   ************************************************************\n"\
           "   Similarity   Course No.   Title                             \n"\
           "   ==========   ==========   ==================================\n"

    sys.stderr.write(menu)
    num_printed = 0
    
    for index in range(max_show + 1):
        ind = res_vector[index]
        similarity = doc_simula[ind]
        title = TITLES[ind][:47]
        code = ID_2_CODE[ind]
        if similarity > 0.01:
            sys.stderr.write("   {0:10.8f}   {1}   {2}\n".format(similarity, code.upper(), title))
            num_printed += 1

    if num_printed == 0:
        print("\n\nNo results found.")
        return

    show_terms = raw_input("\nShow the terms that overlap between the query and "\
        "retrieved docs (y/n): ").strip()
    
    if show_terms != 'n' and show_terms != 'N':
        for index in range(max_show + 1):
            ind = res_vector[index]
            show_overlap(my_qry_vector, COURSE_VECTOR[ind], ind)
            if (index % 5 == 4):
                cont = raw_input("\nContinue (y/n)?: ").strip()
                if cont == 'n' or cont == 'N':
                    break


def show_overlap(my_qry_vector, my_COURSE_VECTOR, ind):
    info = "\n=============================================================\n"\
           " OVERLAPPING TERMS for\n \"{0:10s}\"                         \n"\
           "=============================================================\n"\
           "TERM        QRY_WEIGHT  COURSE_WEIGHT    # of TERMS IN CORPUS\n"\
           "-------------------------------------------------------------\n".format(TITLES[ind])

    sys.stderr.write(info)
    for term_one, weight_one in my_qry_vector.items():
        if my_COURSE_VECTOR.get(term_one, 0):
            info =  "{0:10s}  {1:f}     {2:8f}\t {3}\n".format(
                term_one, weight_one, my_COURSE_VECTOR[term_one], corp_freq_hash[term_one])
            sys.stderr.write(info)
    print("-> Similarity Score: %.10f" %cosine_sim(my_qry_vector, my_COURSE_VECTOR))
    #pdb.set_trace()

def cosine_sim(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
    if not vec1_norm:
        vec1_norm = sum(v * v for v in vec1.values())
    if not vec2_norm:
        vec2_norm = sum(v * v for v in vec2.values())
    
    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1


    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())

    #print(cross_product)
    
    try:
        return cross_product / math.sqrt(vec1_norm * vec2_norm)
    except:
        return 0


def get_course_vect(course_code):
    try:
        return COURSE_VECTOR[CODE_2_ID[course_code]]
    except:
        print("\n*Invalid course number*\n")
        return None

def print_course_vect(course_code):
    try:
        print(COURSE_VECTOR[CODE_2_ID[course_code]])
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



