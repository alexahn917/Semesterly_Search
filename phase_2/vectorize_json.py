import pickle
import json
import re
from collections import defaultdict
from PorterStemmer import PorterStemmer
from pprint import pprint
import math
import numpy as np
from scipy.sparse import linalg
from sklearn import mixture
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.cluster import KMeans
from sklearn import metrics

CODE_2_ID = {}
ID_2_CODE = {}
COURSE_VECTOR = None
COURSE_VECTOR_NORMS = None
TITLES_VECTOR = None
TITLES_VECTOR_NORMS = None
COURSE_CV = None
TITLES_CV = None
TITLES = []
course_vect = []
courses = None

def main():
    global courses
    courses = open("../json_files/preprocessed_courses.json").read()
    courses = json_loads_byteified(courses)
    parse(courses)
    vectorize()
    write_files()

def write_files():
    with open('../pickle/courses.pickle', 'wb') as handle:
        pickle.dump(courses, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/CODE_2_ID.pickle', 'wb') as handle:
        pickle.dump(CODE_2_ID, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/ID_2_CODE.pickle', 'wb') as handle:
        pickle.dump(ID_2_CODE, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/COURSE_VECTOR.pickle', 'wb') as handle:
        pickle.dump(COURSE_VECTOR, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/COURSE_VECTOR_NORMS.pickle', 'wb') as handle:
        pickle.dump(COURSE_VECTOR_NORMS, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/TITLES_VECTOR.pickle', 'wb') as handle:
        pickle.dump(TITLES_VECTOR, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/TITLES_VECTOR_NORMS.pickle', 'wb') as handle:
        pickle.dump(TITLES_VECTOR_NORMS, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/COURSE_CV.pickle', 'wb') as handle:
        pickle.dump(COURSE_CV, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/TITLES_CV.pickle', 'wb') as handle:
        pickle.dump(TITLES_CV, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../pickle/TITLES.pickle', 'wb') as handle:
        pickle.dump(TITLES, handle, protocol=pickle.HIGHEST_PROTOCOL)

def parse(courses):
    global CODE_2_ID
    global ID_2_CODE
    global TITLES
    global course_vect
    
    # containers for courses
    ID = 0
    # create vector models
    for code, course in courses.iteritems():
        CODE_2_ID[course['code']] = ID
        ID_2_CODE[ID] = course['code']
        course_vect.append(parse_course(course['description'], course['instructors'], course['term'], course['year']))
        TITLES.append(parse_title(course['title']))
        ID+=1
        
def vectorize():
    global COURSE_VECTOR
    global COURSE_VECTOR_NORMS
    global TITLES_VECTOR
    global TITLES_VECTOR_NORMS
    global COURSE_CV
    global TITLES_CV

    COURSE_VECTOR_NORMS = []
    TITLES_VECTOR_NORMS = []

    COURSE_CV = CountVectorizer(ngram_range=(1,2), stop_words='english')
    TITLES_CV = CountVectorizer(ngram_range=(1,2))
    course_counts = COURSE_CV.fit_transform(course_vect)
    titles_counts = TITLES_CV.fit_transform(TITLES)

    course_tf = TfidfTransformer(use_idf=False).fit(course_counts)
    COURSE_VECTOR = course_tf.transform(course_counts)
    TITLES_VECTOR = titles_counts

    for i in range(TITLES_VECTOR.shape[0]):
        TITLES_VECTOR_NORMS.append(linalg.norm(TITLES_VECTOR[i,:]))

    for i in range(COURSE_VECTOR.shape[0]):
        COURSE_VECTOR_NORMS.append(linalg.norm(COURSE_VECTOR[i,:]))
    

def parse_title(title):
    #print "TITLE: %s"%title.strip()
    return str(title.strip())

def parse_course(course, instructors, term, year):
    course_str = ""
    if course:
        course_str += (course + " ")
    if instructors:
        course_str += (instructors + " ")
    if term:
        course_str += (term + " ")
    if year:
        course_str += (year)
    #print "COURSE: %s"%course_str
    return str(course_str)

def print_course(course):
    print "\n=========================================="
    print "ID: %s"%course['ID']
    print "CODE: %s"%course['code']
    print "TITLE: %s" %course['title']
    print "DESCRIPTION: %s" %course['description']
    print "INSTRUCTORS: %s" %course['instructors']
    print "TERM: %s" %course['term']
    print "YEAR: %s" %course['year']    

def print_courses(courses):        
    for key, course in courses.iteritems():
        print_course(course)

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