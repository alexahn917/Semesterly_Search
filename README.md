# Semesterly_Search
Search Engine for Semester.ly (currently for Johns Hopkins University courses)

Repository includes...


(1) read_json.py

- python script that reads 'courses.json' file for preprocessing the courses data
	
	outputs:
		1. preprocessed_courses.json


(2) vectorize_json.py

- python script that reads 'preprocessed_courses.json' file for vectorizing documents,
  creating necessary hash and list objects for document modeling.
  
  	outputs:
	  	1. preprocessed_courses.json
	    2. course_vector.json
	    3. titles_vector.json
	    4. course_code2num.json
	    5. course_num2code.json
	    6. docs_freq_hash.json
	    7. corp_freq_hash.json

(3) search.py

- python script that reads necessary json files for document classification/clustering
  script interacts with user for the following 4 options:

  	options:
	    1. Search for courses using a query
	    2. Find most similar courses
	    3. Print course vector model
	    4. Print course information


(4) run.sh

- shell script that runs all of the above.



If there is any question, please contact alexahn917@gmail.com