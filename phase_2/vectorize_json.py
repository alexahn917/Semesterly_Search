import pickle
import json
import re
from collections import defaultdict
import math
import numpy as np
from operator import or_
from scipy.sparse import linalg
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

TITLE_WEIGHT = 10
DESCP_WEIGHT = 3

def main():
    courses = open("../json_files/preprocessed_courses.json").read()
    courses = json_loads_byteified(courses)
    CODE_2_ID, ID_2_CODE, title_vect, descp_vect = parse(courses)
    CV, course_vectors, course_vectors_norms = vectorize(title_vect, descp_vect)
    write_files(courses, CODE_2_ID, ID_2_CODE, CV, course_vectors, course_vectors_norms, title_vect)

def write_files(courses, CODE_2_ID, ID_2_CODE, CV, course_vectors, course_vectors_norms, title_vect):
    with open('./pickle/CODE_2_ID.pickle', 'wb') as handle:
        pickle.dump(CODE_2_ID, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/ID_2_CODE.pickle', 'wb') as handle:
        pickle.dump(ID_2_CODE, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/course_vectors.pickle', 'wb') as handle:
        pickle.dump(course_vectors, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/course_vectors_norms.pickle', 'wb') as handle:
        pickle.dump(course_vectors_norms, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/CV.pickle', 'wb') as handle:
        pickle.dump(CV, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/titles.pickle', 'wb') as handle:
        pickle.dump(title_vect, handle, protocol=pickle.HIGHEST_PROTOCOL)        

def parse(courses):
    CODE_2_ID = {}
    ID_2_CODE = {}
    title_vect = []
    descp_vect = []
    ID = 0
    for code, course in courses.iteritems():
        CODE_2_ID[course['code']] = ID
        ID_2_CODE[ID] = course['code']
        descp_vect.append(str(course['description'].strip()))
        title_vect.append(str(course['title']).strip())
        ID+=1
    return CODE_2_ID, ID_2_CODE, title_vect, descp_vect


def vocabularize(corpus):
    return set([word for doc in corpus for word in tokenizer(doc)])

def tokenizer(doc):
    # Using default pattern from CountVectorizer
    token_pattern = re.compile('(?u)\\b\\w\\w+\\b')
    return [t for t in token_pattern.findall(doc)]

def vectorize(title_vect, descp_vect):
    # vectorize course objects
    vocabulary = reduce(or_, [vocabularize(title_vect), vocabularize(descp_vect)])
    CV = CountVectorizer(ngram_range=(1,2), vocabulary=vocabulary, stop_words='english')    
    descp_counts = CV.transform(descp_vect) * 3
    title_counts = CV.transform(title_vect) * 10
    course_counts = descp_counts + title_counts
    TFIDF_TF = TfidfTransformer(use_idf=False).fit(descp_counts)
    course_vectors = TFIDF_TF.transform(course_counts)

    # calculate norms
    course_vectors_norms = []
    for i in range(course_vectors.shape[0]):
        course_vectors_norms.append(linalg.norm(course_vectors[i,:]))

    return CV, course_vectors, course_vectors_norms

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