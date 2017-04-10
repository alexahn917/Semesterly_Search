import json
import re
from pprint import pprint

def main():
    json_data = open("json_files/courses.json").read()
    json_data = json_loads_byteified(json_data)
    courses = {}
    ID = 0
    ND=0
    NI=0
    i=0
    for course_info in json_data:
        i+=1
        # COURSE block
        if course_info['kind'] == 'course':
            course = dict.fromkeys(['ID', 'code', 'title', 'description', 'instructors', 'term', 'year'])
            course['ID'] = ID
            course['code'] = course_info['code']
            course['title'] = course_info['name']
            ID+=1
            
            if 'description' in course_info:
                descp = ""
                for desc in course_info['description']:
                    descp += desc.strip()
                course['description'] = descp
            else:
                ND+=1
                course['description'] = ""

            # store to object
            courses[course['code']] = course

        # SECTION block
        elif course_info['kind'] == 'section':
            code = course_info['course']['code']
            course = courses[code]
            section_code = course_info['code']
            # add instances for section 01 only
            if section_code == '(01)':
                if 'instructors' in course_info:
                    names = ""
                    for name in course_info['instructors']:
                        names += (name['name'] + " ")
                    course['instructors'] = names
                else:
                    NI+=1
                course['term'] = course_info['term']
                course['year'] = course_info['year']
            # add instructor names for other sections
            else:                
                if 'instructors' in course_info:
                    names = course['instructors']
                    if not names:
                        names = ""
                    for name in course_info['instructors']:
                        names += (name['name'] + " ")
                    course['instructors'] = names
                else:
                    NI+=1
        elif course_info['kind'] == 'meeting':
            continue
        
        else:
            print("ERROR!")

    print "Number of blocks: %d" %i
    print "Number of courses: %d" %ID
    print "Number of missing descriptions: %d" %ND
    print "Number of missing instructor names: %d" %NI

    with open("json_files/preprocessed_courses.json", "w") as f:
        json.dump(courses, f, indent=4)

def print_courses(courses):
    for key, course in courses.iteritems():
        print "\n=========================================="
        print "ID: %s"%course['ID']
        print "CODE: %s"%course['code']
        print "TITLE: %s" %course['title']
        print "DESCRIPTION: %s" %course['description']
        print "INSTRUCTORS: %s" %course['instructors']
        print "TERM: %s" %course['term']
        print "YEAR: %s" %course['year']

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
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

if __name__ == '__main__':
    main()