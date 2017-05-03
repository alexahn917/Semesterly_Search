import pickle
import json
import re
from collections import defaultdict
import math
import numpy as np
from scipy.sparse import linalg
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

def main():
    courses = open("../json_files/preprocessed_courses.json").read()
    courses = json_loads_byteified(courses)
    CODE_2_ID, ID_2_CODE, titles, course_vect = parse(courses)
    CV, course_vector, course_vector_norms = vectorize(titles, course_vect)
    write_files(courses, CODE_2_ID, ID_2_CODE, titles, course_vect, CV, course_vector, course_vector_norms)

def write_files(courses, CODE_2_ID, ID_2_CODE, titles, course_vect, CV, course_vector, course_vector_norms):
    with open('./pickle/courses.pickle', 'wb') as handle:
        pickle.dump(courses, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/CODE_2_ID.pickle', 'wb') as handle:
        pickle.dump(CODE_2_ID, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/ID_2_CODE.pickle', 'wb') as handle:
        pickle.dump(ID_2_CODE, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/course_vector.pickle', 'wb') as handle:
        pickle.dump(course_vector, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/course_vector_norms.pickle', 'wb') as handle:
        pickle.dump(course_vector_norms, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/CV.pickle', 'wb') as handle:
        pickle.dump(CV, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./pickle/titles.pickle', 'wb') as handle:
        pickle.dump(titles, handle, protocol=pickle.HIGHEST_PROTOCOL)

def parse(courses):
    CODE_2_ID = {}
    ID_2_CODE = {}
    titles = []
    course_vect = []
    ID = 0
    for code, course in courses.iteritems():
        CODE_2_ID[course['code']] = ID
        ID_2_CODE[ID] = course['code']
        course_vect.append(str(course['description'].strip()))
        #course_vect.append(parse_course(course['description'], course['instructors'], course['term'], course['year']))
        titles.append(str(course['title']).strip())
        ID+=1    
    return CODE_2_ID, ID_2_CODE, titles, course_vect

        
def vectorize(titles, course_vect):
    CV = CountVectorizer(ngram_range=(1,2), stop_words='english')
    descp_counts = CV.fit_transform(course_vect) * 3
    title_counts = CV.transform(titles) * 10
    course_counts = descp_counts + title_counts
    TFIDF_TF = TfidfTransformer(use_idf=False).fit(descp_counts)
    course_vector = TFIDF_TF.transform(course_counts)

    course_vector_norms = []
    for i in range(course_vector.shape[0]):
        course_vector_norms.append(linalg.norm(course_vector[i,:]))
    
    return CV, course_vector, course_vector_norms

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
    return str(course_str)


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