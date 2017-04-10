import json
import re
from collections import defaultdict
from PorterStemmer import PorterStemmer
from pprint import pprint

def main():
    courses = open("json_files/preprocessed_courses.json").read()
    courses = json_loads_byteified(courses)

    # set up global variables (read_only)
    global poter_stemmer
    global stoplist_hash
    global docs_freq_hash
    global corp_freq_hash
    
    # containers for courses
    course_vector = []
    titles_vector  = []
    course_codes = []
    
    # frequency hashes
    docs_freq_hash = defaultdict(int)
    corp_freq_hash = defaultdict(int)

    # porter stemming
    poter_stemmer = PorterStemmer()

    # create stoplist    
    stoplist_hash = set()
    for line in open("txt_files/common_words.stemmed", 'r'):
        if line:
            stoplist_hash.add(line.strip())

    # Weighting terms by area
    wCODE = 10
    wTITLE = 5
    wDESCRIPTION = 3
    wINSTRUCTORS = 2
    wTERM = 1
    wYEAR = 1
    
    # create vector models
    for code, course in courses.iteritems():

        # create course vector
        course_vect = defaultdict(int)
        course_vector.append(course_vect)
        titles_vector.append(course['title'])
        course_codes.append(code)

        # (1) read code
        course_vect[code] += wCODE
        course_vect[code[3:]] += wCODE

        # (2) read title
        vectorize_string(course['title'], course_vect, wTITLE)

        # (3) read description
        vectorize_string(course['description'], course_vect, wDESCRIPTION)
        
        # (4) read instructors
        vectorize_string(course['instructors'], course_vect, wINSTRUCTORS)
        
        # (5) read term/year
        vectorize_string(course['term'], course_vect, wTERM)
        vectorize_string(course['year'], course_vect, wYEAR)

    # write to json files
    with open("json_files/course_vector.json", "w") as f:
        json.dump(course_vector, f, indent=4)

    with open("json_files/titles_vector.json", "w") as f:
        json.dump(titles_vector, f, indent=4)

    with open("json_files/course_codes.json", "w") as f:
        json.dump(course_codes, f, indent=4)

    with open("json_files/docs_freq_hash.json", "w") as f:
        json.dump(docs_freq_hash, f, indent=4)
    
    with open("json_files/corp_freq_hash.json", "w") as f:
        json.dump(corp_freq_hash, f, indent=4)        


########################################################
## vectorize_string(string, course, weight)
##
##
## a function that converts a large string value
## into tokens of valid words, which is added to
## course vector (dict) with proper weights.
##
########################################################
def vectorize_string(string, course_vect, WEIGHT):
    if not string:
        return

    special_chars = ['\r', '\n', '\t']
    for special_char in special_chars:
        string = string.replace(special_char, " ")

    prev = ""
    for word in string.split(' '):
        word = word.strip()
        if re.search('[a-zA-Z]', word):
            word = word.lower()
            word = poter_stemmer.stem(word, 0, len(word)-1)
            if word not in stoplist_hash:
                course_vect[word] += WEIGHT
                corp_freq_hash[word] += 1
                if word not in docs_freq_hash:
                    docs_freq_hash[word] = 1
        if prev:
            if prev not in stoplist_hash and word not in stoplist_hash:
                bigram = prev + " " + word

                course_vect[bigram] += WEIGHT
                corp_freq_hash[bigram] += 1
                if bigram not in docs_freq_hash:
                    docs_freq_hash[bigram] = 1
        prev = word

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