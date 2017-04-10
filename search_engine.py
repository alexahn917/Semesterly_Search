#!/usr/bin/env python
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

# Containers
doc_vector = []
qry_vector = []
corp_freq_hash = defaultdict(int)
docs_freq_hash = defaultdict(int)
#relevance_hash = defaultdict(lambda: defaultdict(int))
stoplist_hash = set()
titles_vector  = []
doc_simula = []
res_vector = []

sys.stderr.write("INITIALIZING VECTORS ... \n")

# Stopwords
for line in open("common_words.stemmed", 'r'):
    if line:
        stoplist_hash.add(line.strip())

# File Reading
json_data=open("courses.json").read()
data = json.loads(json_data)

# Stemming
p = PorterStemmer()

TITLE = 2
DESC = 1

docs_freq_hash = {}
corp_freq_hash = {}

doc_vector.append(defaultdict(int))
titles_vector.append("")

ID = 0

for line in data:
    course = {}

    if line['kind'] == 'course':
        ID+=1
        course = {}
        #courses[line['code']] = course
        course['ID'] = ID
        course['code'] = line['code']
        course['title'] = line['name']
        try:
            course['description'] = line['description']
        except:
            course['description'] = ""
    if line['kind'] == 'meeting':
        course['instructors'] = 

for course in courses:        
        doc_vect = {}
        terms = set()
        doc_vector.append(doc_vect)
        titles_vector.append(course['code'] + "   " + course['title'])

        title_word_vect = course['title'].split(" ")
        descp_word_vect = str(course['description']).split(' ')
        
        prev = ""
        for title_word in title_word_vect:
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
                bigram = prev+" "+title_word
                if bigram not in doc_vect:
                    doc_vect[bigram] = TITLE
                else:
                    doc_vect[bigram] += TITLE

                if bigram not in corp_freq_hash:
                    corp_freq_hash[bigram] = 1
                else:
                    corp_freq_hash[bigram] += 1
                terms.add(bigram)
            prev = title_word

        prev = ""
        for descp_word in descp_word_vect:
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
                bigram = prev+" "+descp_word
                if bigram not in doc_vect:
                    doc_vect[bigram] = DESC
                else:
                    doc_vect[bigram] += DESC

                if bigram not in corp_freq_hash:
                    corp_freq_hash[bigram] = 1
                else:
                    corp_freq_hash[bigram] += 1
                terms.add(bigram)
            prev = descp_word

        for term in terms:
            if term not in docs_freq_hash:
                docs_freq_hash[term] = 1
            else:
                docs_freq_hash[term] += 1

total_docs = ID

# Using Thesures(Synonyms)
synonyms = {}
synonyms_list = []
useThesures = True
if useThesures:
    p = PorterStemmer()
    with open("synonyms_short.txt", 'r') as f:
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

    new_qry_vect = []

    for qry_vect in qry_vector:
        new_vect = defaultdict(int)
        for key in qry_vect:
            new_vect[key] = qry_vect[key]
            if key in synonyms:
                sim_words_list = synonyms_list[synonyms[key]]
                for sim_word in sim_words_list:
                    if sim_word not in stoplist_hash and re.search("[a-zA-z]", sim_word):
                        if corp_freq_hash[sim_word] > 1:
                            new_vect[sim_word] = qry_vect[key]
        new_qry_vect.append(new_vect)
    qry_vector = new_qry_vect


# TF_IDF weighting
def to_TF_IDF_weighting():
    for i in range(1, len(doc_vector)):
        for term in doc_vector[i]:
            doc_vector[i][term] *= math.log(total_docs / docs_freq_hash[term])
            
def to_boolean_weighting():
    for i in range(1, len(doc_vector)):
        for term in doc_vector[i]:
            doc_vector[i][term] = 1

##########################################################
## MAIN_LOOP
##
## Parameters: currently no explicit parameters.
##             performance dictated by user imput.
##
## Initializes document and query vectors using the
## input files specified in &init_files. Then offers
## a menu and switch to appropriate functions in an
## endless loop.
##
## Possible extensions at this level:  prompt the user
## to specify additional system parameters, such as the
## similarity function to be used.
##
## Currently, the key parameters to the system (stemmed/unstemmed,
## stoplist/no-stoplist, term weighting functions, vector
## similarity functions) are hardwired in.
##
## Initializing the document vectors is clearly the
## most time consuming section of the program, as 213334
## to 258429 tokens must be processed, weighted and added
## to dynamically growing vectors.
##
##########################################################

def main():
    menu = \
    "============================================================\n"\
    "==      Welcome to the Semester.ly's Search Engine          \n"\
    "==                                                          \n"\
    "==      Total Number of Courses: {0}                                \n"\
    "============================================================\n"\
    "                                                            \n"\
    "OPTIONS:                                                    \n"\
    "  1 = Find documents most similar to a given query or document\n"\
    "  2 = Compute precision/recall for the full query set         \n"\
    "  3 = Compute cosine similarity between two queries/documents \n"\
    "  4 = Quit                                                    \n"\
    "                                                              \n"\
    "============================================================\n".format(total_docs)

    to_TF_IDF_weighting()
    #to_boolean_weighting()

    while True:
        sys.stderr.write(menu)
        option = raw_input("Enter Option: ")
        if option == "1":
            get_and_show_retrieved_set()
        elif option == "2":
            full_precision_recall_test()
        elif option == "3":
            do_full_cosine_similarity()
        elif option == "4":
            exit(0)
        else:
            sys.stderr.write("Input seems not right, try again\n")


##########################################################
## GET_AND_SHOW_RETRIEVED_SET
##
##  This function requests key retrieval parameters,
##  including:
##
##  A) Is a query vector or document vector being used
##     as the retrieval seed? Both are vector representations
##     but they are stored in different data structures,
##     and one may optionally want to treat them slightly
##     differently.
##
##  B) Enter the number of the query or document vector to
##     be used as the retrieval seed.
##
##     Alternately, one may wish to request a new query
##     from standard input here (and call the appropriate
##     tokenization, stemming and term-weighting routines).
##
##  C) Request the maximum number of retrieved documents
##     to display.
##
##########################################################

def get_and_show_retrieved_set():
    menu = "Find documents similar to:  \n"\
           "(1) a keyboard-interactive query    \n"\
           "(2) a retrieval of most similar courses    \n"\

    sys.stderr.write(menu)
    comp_type = raw_input("Choice: ")

    if re.match("[123]\s$", comp_type):
        sys.stderr.write("The input is not valid. By default use option 1\n")
        comp_type = "1"

    #max_show = int(raw_input("Show how many matching documents (e.g. 20): "))
    
    if comp_type == "1":
        sys.stderr.write("Interactive Keyboard Query to Document comparison\n")
        int_vector = convert_keyboard_query()
        get_retrieved_set(int_vector)
        shw_retrieved_set(15, 0, int_vector, "Interactive Query")

    if comp_type == "2":
        sys.stderr.write("Retrieving most similar courses to the selected one\n")
        comp_type = raw_input("Choice: ")
        int_vector = doc_vector[int(comp_type)]
        get_retrieved_set(int_vector)
        shw_retrieved_set(15, 0, int_vector, "Interactive Query")        

def convert_keyboard_query():
    qry = raw_input("Type in your query:")
    words = qry.strip().split(' ')
    p = PorterStemmer()
    QUERY_WEIGHT = 2
    new_doc_vec = defaultdict(int)

    prev = ""
    for word in words:
        word = word.strip()
        if re.search('[a-zA-Z]', word):
            word = word.lower()
            word = p.stem(word, 0, len(word)-1)
            if word in new_doc_vec:
                new_doc_vec[word] += QUERY_WEIGHT
            elif word not in stoplist_hash and word in corp_freq_hash:
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

    new_vect = defaultdict(int)
    for key in new_doc_vec:
        new_vect[key] = new_doc_vec[key]
        if key in synonyms:
            sim_words_list = synonyms_list[synonyms[key]]
            for sim_word in sim_words_list:
                if sim_word not in stoplist_hash and re.search("[a-zA-z]", sim_word):
                    if corp_freq_hash[sim_word] > 1:
                        new_vect[sim_word] = new_doc_vec[key]
    print new_vect
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
    
    tot_number = len(doc_vector) - 1

    doc_simula = []   # insure that storage vectors are empty before we
    res_vector = []   # calculate vector similarities

    doc_simula.append(0)

    for index in range(1, tot_number + 1):
        doc_simula.append(cosine_sim_a(my_qry_vector, doc_vector[index]))

    res_vector = sorted(range(1, tot_number + 1), key = lambda x: -doc_simula[x])

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
    for index in range(max_show + 1):
        ind = res_vector[index]
        if comparison == "Query" and relevance_hash[qry_num][ind]:
            sys.stderr.write("* ")
        else:
            sys.stderr.write("  ")

        similarity = doc_simula[ind]
        title = titles_vector[ind][:47]
        if similarity > 0.01:
            sys.stderr.write(" {0:10.8f}   {1}\n".format(similarity, title))

    show_terms = raw_input("\nShow the terms that overlap between the query and "\
        "retrieved docs (y/n): ").strip()
    if show_terms != 'n' and show_terms != 'N':
        for index in range(max_show + 1):
            ind = res_vector[index]

            show_overlap(my_qry_vector, doc_vector[ind], qry_num, ind)

            if (index % 5 == 4):
                cont = raw_input("\nContinue (y/n)?: ").strip()
                if cont == 'n' or cont == 'N':
                    break


##########################################################
## SHOW_RELVNT
##
## This function should take the rank orders and similarity
## arrays described in &show_retrieved_set and &comp_recall
## and print out only the relevant documents, in an order
## and manner of presentation very similar to &show_retrieved_set.
##########################################################

def show_relvnt(relevance_qry_hash, vect_num, my_qry_vector):
    menu = "   ------------------------------------------------------------\n"\
           "                        Relevant Documents       \n"\
           "   ------------------------------------------------------------\n"\
           "   Similarity   Course No.   Title                             \n"\
           "   ==========   ==========   ==================================\n"

    sys.stderr.write(menu)
    for doc_num in docs_sorted_by_similarity:
        sys.stderr.write("* ")
        similarity = doc_simula[doc_num]
        title = titles_vector[doc_num][:47]
        sys.stderr.write(" {0:10.8f}   {1}\n".format(similarity, title))

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


def show_overlap(my_qry_vector, my_doc_vector, qry_num, doc_num):
    info = "============================================================\n"\
           "{0:15s}  {1:8d}   {2:8d}\t{3}\n"\
           "============================================================\n".format(
            "Vector Overlap", qry_num, doc_num, "Docfreq")
    sys.stderr.write(info)
    for term_one, weight_one in my_qry_vector.items():
        if my_doc_vector.get(term_one, 0):
            info =  "{0:15s}  {1:f}   {2:8f}\t{3}\n".format(
                term_one, weight_one, my_doc_vector[term_one], corp_freq_hash[term_one])
            sys.stderr.write(info)


##########################################################
## COMPUTE_PREC_RECALL
##
## Like "shw_retrieved_set", this function makes use of the following
## data structures which may either be passed as parameters or
## used as global variables. These values are set by the function
## &get_retrieved_set.
##
## 1) res_vector - contains the document numbers sorted in
##                  rank order
##
## 2) doc_simula - The similarity measure for each document,
##                  computed by &get_retrieved_set.
##
## Also assumes that the following have been initialzied in advance:
##       titles[ docn ]       - the document title for a document
##                                number $docn
##       relevance_hash[ qvn ][ docn ]
##                              - is $docn relevant given query number
##                                $qvn
##
##  The first step of this function should be to take the rank ordering
##  of the documents given a similarity measure to a query
##  (i.e. the list docs_sorted_by_similarity[rank]) and make a list
##  of the ranks of just the relevant documents. In an ideal world,
##  if there are k=8 relevant documents for a query, for example, the list
##  of rank orders should be (1 2 3 4 5 6 7 8) - i.e. the relevant documents
##  are the top 8 entries of all documents sorted by similarity.
##  However, in real life the relevant documents may be ordered
##  much lower in the similarity list, with rank orders of
##  the 8 relevant of, for example, (3 27 51 133 159 220 290 1821).
##
##  Given this list, compute the k (e.g. 8) recall/precison pairs for
##  the list (as discussed in class). Then to determine precision
##  at fixed levels of recall, either identify the closest recall
##  level represented in the list and use that precision, or
##  do linear interpolation between the closest values.
##
##  This function should also either return the various measures
##  of precision/recall specified in the assignment, or store
##  these values in a cumulative sum for later averaging.
##########################################################


def comp_recall(relevance_qry_hash, vect_num, isFull):
    global docs_sorted_by_similarity

    docs_sorted_by_similarity = []
    rel_docs = set()
    for doc_num in res_vector:
        if relevance_qry_hash[doc_num]:
            docs_sorted_by_similarity.append(doc_num)
            rel_docs.add(doc_num)

    N = total_docs
    Rel = len(docs_sorted_by_similarity)

    #print "\nCalculating precision/recalls for %d retrieved documents for query %d\n" %(k, vect_num)

    prec_25 = 0.0
    prec_50 = 0.0
    prec_75 = 0.0
    prec_25_idx = int(Rel*(1.0/4))
    prec_50_idx = int(Rel*(2.0/4))
    prec_75_idx = int(Rel*(3.0/4))
    precision_array = []

    num_retrieved = 0
    i = 1.0
    while num_retrieved < Rel:
        doc_num = res_vector[int(i-1)]
        if doc_num in rel_docs:
            num_retrieved+=1.0
        precision_array.append(float(num_retrieved / i))
        i+=1.0

    prec_25 = precision_array[prec_25_idx]
    prec_50 = precision_array[prec_50_idx]
    prec_75 = precision_array[prec_75_idx]
    prec_100 = precision_array[-1]

    prec_mean_1 = (prec_25 + prec_50 + prec_75) / 3.0

    by_10 = np.arange(0.0, Rel, (Rel+0.0)/10.0)
    by_10 = [int(idx) for idx in by_10]
    prec_mean_2 = 0.0
    for i in by_10:
        prec_mean_2 += precision_array[i]
    prec_mean_2 = prec_mean_2/10

    rank_sum = 0.0
    rank_log_sum = 0.0

    k_i = 1
    for i in range(len(res_vector)):
        if res_vector[i] in rel_docs:
            rank_sum += (i+1) - (k_i)
            rank_log_sum += math.log(i+1) - math.log(k_i)
            k_i+=1

    recall_norm = 1.0 - ( rank_sum / (Rel * (N - Rel)) )

    prec_norm = 1.0 - (rank_log_sum / 
        ( N * math.log(N) - (N - Rel) * math.log(N - Rel) - (Rel) * math.log(Rel) ))

    results = "   ----------------------------------------------------------------\n"\
           "                       Precision & Recall Results                  \n"\
           "   ----------------------------------------------------------------\n"\
           "   P.25   P.50   P.75   P1.00   P_mean1   P_mean2.  P_norm  R_norm\n"\
           "   ====   ====   ====   =====   =======   ========  ======  ======\n"\
           "   %.2f   %.2f   %.2f   %.2f    %.4f    %.4f    %.3f   %.3f   \n"\
               %(prec_25, prec_50, prec_75, prec_100, prec_mean_1, prec_mean_2, prec_norm, recall_norm)
    if not isFull:
        sys.stderr.write(results)
    return (prec_25, prec_50, prec_75, prec_100, prec_mean_1, prec_mean_2, prec_norm, recall_norm)

########################################################
## DO_FULL_COSINE_SIMILARITY
##
##  Prompts for a document number and query number,
##  and then calls a function to show similarity.
##
##  Could/should be expanded to handle a variety of
##  similarity measures.
########################################################

def do_full_cosine_similarity():
    num_one = int(raw_input("\n1st is Query number: ").strip())
    num_two = int(raw_input("\n2nd is Document number: ").strip())
    full_cosine_similarity(qry_vector[num_one], doc_vector[num_two], num_one, num_two)

########################################################
## FULL_COSINE_SIMILARITY
##
## TODO
##
## This function should compute cosine similarity between
## two vectors and display the information that went into
## this calculation, useful for debugging purposes.
## Similar in structure to &show_overlap.
########################################################


def full_cosine_similarity(vec1, vec2, num_one, num_two):
    info = "============================================================\n"\
           "             Full Cosine Similarity Calculations            \n"\
           "               Between Query%d and Document %d              \n"\
           "============================================================\n"%(num_one, num_two)

    sys.stderr.write(info)
    
    vec1_norm = sum(v * v for v in vec1.values())
    vec2_norm = sum(v * v for v in vec2.values())

    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1

    # calculate the cross product
    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
    print "Vector 1 normalizing constant (squared) : %f" %vec1_norm
    print "Vector 2 normalizing constant (squared) : %f" %vec2_norm
    print "Cross product between two vectors : %f" %cross_product
    print "Cosine Similarity: %f" %(cross_product / math.sqrt(vec1_norm * vec2_norm))
    return cross_product / math.sqrt(vec1_norm * vec2_norm)    


##########################################################
##  FULL_PRECISION_RECALL_TEST
##
##  This function should test the various precision/recall
##  measures discussed in the assignment and store cumulative
##  statistics over all queries.
##
##  As each query takes a few seconds to process, print
##  some sort of feedback for each query so the user
##  has something to watch.
##
##  It is helpful to also log this information to a file.
##########################################################

def full_precision_recall_test():
# Suggestion: if using global variables to store cumulative
#             statistics, initialize them in the begining of .
#             script
    combined_results = "   ----------------------------------------------------------------\n"\
           "                   Total Precision & Recall Results                  \n"\
           "   ----------------------------------------------------------------\n"\
           "   Q#  P.25   P.50   P.75   P1.00   P_mean1   P_mean2.  P_norm  R_norm\n"\
           "   ==  ====   ====   ====   =====   =======   ========  ======  ======\n"
    #sys.stderr.write(combined_results)

    total_scores = [0.0] * 8

    for ind in range(1, total_qrys + 1):
        get_retrieved_set( qry_vector[ind] )
        result = comp_recall( relevance_hash[ ind ], ind , True)
        show = "   %2d  %.2f   %.2f   %.2f   %.2f    %.4f    %.4f    %.3f   %.3f   \n"\
               %(ind, result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])
        #sys.stderr.write(show)
        
        for i in range(8):
            total_scores[i] += result[i]

    for i in range(8):
        total_scores[i] /= total_qrys

    averaged_results = "   ----------------------------------------------------------------\n"\
           "                          Averaged Results                         \n"\
           "   ----------------------------------------------------------------\n"\
           "   **  P.25   P.50   P.75   P1.00   P_mean1   P_mean2.  P_norm  R_norm\n"\
           "   ==  ====   ====   ====   =====   =======   ========  ======  ======\n"\
           "   %2d  %.2f   %.2f   %.2f   %.2f    %.4f    %.4f    %.3f   %.3f   \n"\
               %(total_qrys, total_scores[0], total_scores[1], total_scores[2], total_scores[3], total_scores[4], total_scores[5], total_scores[6], total_scores[7])
    sys.stderr.write(averaged_results)


########################################################
## COSINE_SIM_A
##
## Computes the cosine similarity for two vectors
## represented as associate arrays. You can also pass the
## norm as parameter
##
## Note: You may do it in a much efficient way like
## precomputing norms ahead or using packages like
## "numpy", below provide naive implementation of that
########################################################

def cosine_sim_a(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):

    if not vec1_norm:
        vec1_norm = sum(v * v for v in vec1.values())
    if not vec2_norm:
        vec2_norm = sum(v * v for v in vec2.values())
    
    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1

    # calculate the cross product
    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
    return cross_product / math.sqrt(vec1_norm * vec2_norm)

########################################################
##  COSINE_SIM_B
##  Same thing, but to be consistant with original perl
##  script, we add this line
########################################################
def cosine_sim_b(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
    return cosine_sim_a(vec1, vec2, vec1_norm, vec2_norm)

def dice_sim(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
    if not vec1_norm:
        vec1_norm = sum(v for v in vec1.values())
    if not vec2_norm:
        vec2_norm = sum(v for v in vec2.values())
    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1
    # calculate the cross product
    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
    return 2 * cross_product / (vec1_norm + vec2_norm)

def jaccard_sim(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
    if not vec1_norm:
        vec1_norm = sum(v for v in vec1.values())
    if not vec2_norm:
        vec2_norm = sum(v for v in vec2.values())
    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1
    # calculate the cross product
    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
    return cross_product / (vec1_norm + vec2_norm - cross_product)

def overlap_sim(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
    if not vec1_norm:
        vec1_norm = sum(v for v in vec1.values())
    if not vec2_norm:
        vec2_norm = sum(v for v in vec2.values())
    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1
    # calculate the cross product
    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
    return cross_product / min(vec1_norm, vec2_norm)

if __name__ == "__main__": main()









