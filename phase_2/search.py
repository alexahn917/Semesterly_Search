import pickle
import sys
import re
import os
import subprocess
import math
import numpy as np
import pdb
import json
import pdb
from bs4 import BeautifulSoup
import requests
from scipy.sparse import linalg
from PorterStemmer import PorterStemmer
from collections import defaultdict

CODE_2_ID = None
ID_2_CODE = None
titles = None
courses = None
course_vector = None
course_vector_norms = None
CV = None
doc_simula = []
res_vector = []
N = 0

def load_pickles():
    global CODE_2_ID
    global ID_2_CODE
    global titles
    global courses
    global course_vector
    global course_vector_norms
    global CV
    global N

    with open('./pickle/courses.pickle', 'wb') as handle:
        courses = pickle.load(handle)
    with open('./pickle/CODE_2_ID.pickle', 'wb') as handle:
        CODE_2_ID = pickle.load(handle)
    with open('./pickle/ID_2_CODE.pickle', 'wb') as handle:
        ID_2_CODE = pickle.load(handle)
    with open('./pickle/course_vector.pickle', 'wb') as handle:
        course_vector = pickle.load(handle)
    with open('./pickle/course_vector_norms.pickle', 'wb') as handle:
        course_vector_norms = pickle.load(handle)
    with open('./pickle/CV.pickle', 'wb') as handle:
        CV = pickle.load(handle)
    with open('./pickle/titles.pickle', 'wb') as handle:
        titles = pickle.load(handle)
    
    N = COURSE_VECTOR.shape[0]
    #pdb.set_trace()
    
def main():
    load_pickles()

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
            print_course_vect(code.upper())
        elif option == "4":
            code = raw_input("Enter Code: ")
            print_course_info(code.upper())
        elif option == "5":
            exit(0)
        else:
            sys.stderr.write("Invalid input, please try again\n")


def search():
    max_show = 15 #int(raw_input("Show how many matching documents (e.g. 20): "))
    qry, titles_qry, course_qry = convert_keyboard_query()
    queries = [qry, titles_qry, course_qry]
    get_retrieved_set(queries)
    shw_retrieved_set(queries)


def find_similar_courses():
    #sys.stderr.write("Retrieving most similar courses to the selected one\n")
    comp_type = raw_input("Type Course Code (XX.###.###): ")
    try:
        course_vect = COURSE_VECTOR[CODE_2_ID[comp_type.upper()]]
    except:
        print("\n*Invalid course code*\n")
        return
    get_retrieved_set([course_vect])
    shw_retrieved_set([course_vect])      


def convert_keyboard_query():
    qry = raw_input("Search Semeter.ly : ").lower()
    titles_qry = TITLES_CV.transform([qry])
    course_qry = COURSE_CV.transform([qry])
    return qry, titles_qry, course_qry


def get_retrieved_set(queries):
    global doc_simula, res_vector
    doc_simula = []   # insure that storage vectors are empty before we
    res_vector = []   # calculate vector similarities
    for index in range(N):
        doc_simula.append(calculate_similarity(queries, index))
    res_vector = sorted(range(N), key = lambda x: -doc_simula[x])


def shw_retrieved_set(queries):
    menu = "   ************************************************************\n"\
           "                        Most Similar Courses                   \n"\
           "   ************************************************************\n"\
           "   Similarity   Course No.   Title                             \n"\
           "   ==========   ==========   ==================================\n"

    sys.stderr.write(menu)
    num_printed = 0
    max_show = 10
    for index in range(max_show + 1):
        ind = res_vector[index]
        similarity = doc_simula[ind]
        title = TITLES[ind][:47]
        code = ID_2_CODE[ind]
        if similarity > 0.01:
            sys.stderr.write(" {0:10.8f}   {1}   {2}\n".format(similarity, code.upper(), title))
            num_printed += 1

    if num_printed == 0:
        print("\n\nNo results found.")
        return

#    show_terms = raw_input("\nShow the terms that overlap between the query and "\
#        "retrieved docs (y/n): ").strip()
#    
#    if show_terms != 'n' and show_terms != 'N':
#        for index in range(max_show + 1):
#            ind = res_vector[index]
#            show_overlap(queries, COURSE_VECTOR[ind], ind)
#            if (index % 5 == 4):
#                cont = raw_input("\nContinue (y/n)?: ").strip()
#                if cont == 'n' or cont == 'N':
#                    break
#

#def show_overlap(queries, course_vect, doc_num):
#    info = "============================================================\n"\
#           "{0:15s}  {1:8d}   {2:8d}\t{3}\n"\
#           "============================================================\n".format(
#            "Vector Overlap", qry_num, doc_num, "Docfreq")
#    sys.stderr.write(info)
#    for term_one, weight_one in queries.items():
#        if course_vect.get(term_one, 0):
#            info =  "{0:15s}  {1:f}   {2:8f}\t{3}\n".format(
#                term_one, weight_one, course_vect[term_one], corp_freq_hash[term_one])
#            sys.stderr.write(info)


def calculate_similarity(queries, index):
    if len(queries) == 1:
        return cosine_sim(queries[0], COURSE_VECTOR[index], 0.0, COURSE_VECTOR_NORMS[index], "course")
    else:
        score = cosine_sim(queries[0], TITLES[index], 0.0, 0.0, "raw_qry")
        score += cosine_sim(queries[1], TITLES_VECTOR[index], 0.0, TITLES_VECTOR_NORMS[index], "titles_qry")
        score += cosine_sim(queries[0], COURSE_VECTOR[index], 0.0, COURSE_VECTOR_NORMS[index], "course")
        return score

def cosine_sim(qry, vec2, qry_norm, vec2_norm, qry_type):
    if qry_type == "course":
        return 0

    elif qry_type == "raw_qry":
        count=0
        if qry in vec2.lower():
            return 1
        else:
            return 0
#        qry_words = qry.split()
#        title_words = vec2.lower().split()
#        for title_word in title_words:
#            for qry_word in qry_words:
#                if qry_word in title_word:
#                    count+=1
#        if count == len(qry_words):
#            return 1
#        else:
#            return 0

    elif qry_type == "titles_qry":
        return 0

    elif qry_type == "course_qry":
        return 0

    else:
        print("WRONG QRY TYPE")
        exit(1)

    if not qry_norm:
        #qry_norm = sum(linalg.norm(qry[,:]))
        print("calculating qry_norm")
        exit(1)
    if not vec2_norm:
        print("vec2 norm: should never enter here.")
        exit(1)
        vec2_norm = sum(v * v for v in vec2.values())
    
    print("CALCULATE COSINE SIM:")
    exit(1)
    # save some time of iterating over the shorter vec
    if qry.shape[1] > vec2.shape[1]:
        qry, vec2 = vec2, qry

    # calculate the cross product
    cross_product = sum(qry.get(term, 0) * vec2.get(term, 0) for term in qry.keys())
    try:
        return cross_product / math.sqrt(qry_norm * vec2_norm)
    except:
        return 0

def print_course_vect(course_code):
    try:
        print(COURSE_CV.decode(COURSE_VECTOR[CODE_2_ID[course_code]]))
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

if __name__ == '__main__':
    main()



