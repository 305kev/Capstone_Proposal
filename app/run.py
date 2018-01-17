# RM NOTE: to run, run the following command from the ./app directory
# export FLASK_APP=run.py && python -m flask run

from flask import Flask, url_for, render_template, request, json, jsonify, Response
import os
import _pickle as cPickle
import copy
import sys
sys.path.append('/Users/kevingmagana/DSI/capstone/capstone-update/Capstone_Proposal/py_scripts/')
import results
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


#NOTES FOR KEVIN
# here, try loading your pickled model into a variable, then when you run the flask application, it should be available in the function below
# EXAMPLE
# model = load_model()

model = results.load_model()
def process_query(query):
    """
    :param query: string, the query
    :return: list, of indices or DOC IDs
      EX:
      	 [2939, 4213, 3703, 695, 1810, 3397, 3311, 2663, 177, 1587]
    """
    # Step 1: Intake and get Indexed Cases
    query =  query
    indices = results.indexed_results(model[0], query)
    # Step 2: Get index_vectors and case_val dictionary
    index_vectors, case_value_dictionary= results.get_index_vectors(model[2], indices)
    # Step 3: Vectorize query
    vectorized_query = results.query_vector(model[1], query)
    # Step 4: Get Cosine similarities
    cosine_similarities = results.cosine_similarity(vectorized_query, index_vectors)
    # Step 5: Get top results and rank them (top 10 right now...)
    top_results = (results.get_top_values(cosine_similarities[0], 10), query)
    res = [case_value_dictionary[array_value] for array_value in top_results[0]]
    return res

def clean_text(case_text):
	"""
    :param case_text: list of strings (case_text)
    :return: list of lists of strings (stemmed words)
    """

	table = str.maketrans({key: None for key in string.punctuation})
	tokenized = [word_tokenize(case.translate(table).lower()) for case in case_text]
	stop = set(stopwords.words('english'))
	remove_stop_words = [[word for word in words if word not in stop] for words in tokenized]
	snowball = SnowballStemmer('english')
	## Stemmed words
	return [[snowball.stem(word) for word in words] for words in remove_stop_words]


def get_most_relevant_part(case_index, corpus_df, query, top_n=3, highlight_num=1):
	"""
    :param case_index: int, the index of the case
    :param corpus_df: pandas dataframe, for the entire corpus of cases
    :param query: string, of the web-input query
    :param top_n: int, the top n matching paragraphs with query
    :returns highlight_output: if highlight_num == 1, a single string (most relevant part)
    		else if highlight_num > 1, a list of strings (top 2 or 3 most relevant parts)

    Two use cases:
        (1) if highlight_num == 1 then it's to return for single highlighting.
            See highlight_key_query_words() for example.
        (2) if highlight_num > 1 then this function is for returning the list of 3 most
        relevant parts of a text to be highlighted once a user clicks on the search result.

    """
	## Step 1: Load up the data frame
	html = corpus_df.html_format[case_index]
	soup = BeautifulSoup(html, 'lxml')

	## Step 2: Parse the case into a list of strings
	list_of_paragraphs = []
	for paragaph in soup.findAll('p'):
		list_of_paragraphs.append(paragaph.getText())

	## Step 3: Parse case and vectorize with Tf-IDF weights
	cleaned_text = clean_text(list_of_paragraphs)
	list_of_strings = [" ".join(lst) for lst in cleaned_text]
	vectorizer = TfidfVectorizer(stop_words='english')
	vectors = vectorizer.fit_transform(list_of_strings)

	## Step 4: Vectorize Query
	query_list = [query]
	cleaned_query = clean_text(query_list)
	query_list_of_strings = [" ".join(lst) for lst in cleaned_query]
	tokenized_query = vectorizer.transform(query_list_of_strings)

	## Step 5: Run Cosine Similarity on Query and Case Text
	cosine_similarities = linear_kernel(tokenized_query, vectors)
	top_results = [i for i in np.argsort(cosine_similarities[0])[-1:-top_n - 1:-1]]

	if highlight_num == 1:
		highlight_output = list_of_paragraphs[top_results[0]]
	elif highlight_num == 2:
		highlight_output = [list_of_paragraphs[ind] for ind in top_results[0:2]]
	else:
		highlight_output = [list_of_paragraphs[ind] for ind in top_results[0:3]]
	return highlight_output  ## Returns top 3 indexed cases

def highlight_key_query_words(question, most_relevant_part):
	"""
	:param question:
	:param most_relevant_part:
	:return:
	"""
	# print(question)
	# print(most_relevant_part)
	final_results = []
	stop = set(stopwords.words('english'))
	parse_query = "".join(question).split(' ')
	parse_query = clean_text(parse_query)

	most_relevant = most_relevant_part.split(' ')
	check_result = clean_text(most_relevant)
	# print(len(most_relevant))
	# print(len(check_result))
    #
	# print(most_relevant)
	# print(check_result)

	for ind, word in enumerate(most_relevant):
		if check_result[ind] in parse_query and check_result[ind] != []:
			final_results.append('<b>' + word + '</b>')
		else:
			final_results.append(word)
	return " ".join(('...', ' '.join(final_results), '<b>' + '... Continue reading case' + '</b>' ))

def get_relevant_info(list_of_case_indices, df, legal_query):
	"""
	:param list_of_case_indices: list of all ranked case indices.
	:param df: dataframe, of all the court cases
	:return: json,

		EX:
			[ {
                    case_id: 1,
                    case_title: “Roe V Wade Supreme Court United States”,
                    case_date: “1970-10-01",
                    case_text: “The types of law pose a domain-knowledge  legal document types. ... ”,
                    case_html: sampleDiv,
                    case_matches: [“flat inconsistency between the contemporary statement
                    and the later statement”, “was sufficient” ]
                }, ]

	"""
	# Initialize a relevant info list
	relevant_info = []
	# create instances for filling up relevant info lis
	print(list_of_case_indices)
	for index in list_of_case_indices:
		results = get_most_relevant_part(index, df, legal_query, top_n=3, highlight_num=1)
		highlights = highlight_key_query_words(legal_query,results)
		matches = get_most_relevant_part(index, df, legal_query, top_n=3, highlight_num=3)

		index = np.asscalar(index)
		empDict = {
			'case_id': index,
			'case_title': df.case_title[index],
			'case_date': df.date[index],
			'case_text': highlights,
			'case_html': df.html_format[index],
			'case_matches': matches

		}

		relevant_info.append(empDict)

	# convert to json data
	jsonStr = json.dumps(relevant_info)

	return Response(jsonStr, mimetype='application/json')


@app.route('/')
def root():
	return render_template("index.html")


@app.route("/get_results", methods=["POST"])
def get_results():
	# here, do something to prove that the model has been loaded in memory
	# when you started the application, and persists in memory, get results
	# will be called everytime that you hit search on the front-end, i
	# recommend printing out something here that proves that your pickled
	# data is loaded, and does not have to be loaded again; once we know
	# this, we'll be safe to assume that we won't have to wait the extra
	#  2 - 3 minutes when we demo
	# EXAMPLE

	# print (model)
	# print(type(request.form))
	imd = request.form  ## Dictionary -
	dict_results = imd.to_dict(flat=False)
	input_query = ''.join(list(dict_results))
	ranked_indices = process_query(input_query)

	return get_relevant_info(ranked_indices, model[3], input_query)##JSON FILE




