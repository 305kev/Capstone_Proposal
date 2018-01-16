# RM NOTE: to run, run the following command from the ./app directory
# export FLASK_APP=run.py && python -m flask run

from flask import Flask, url_for, render_template, request, json, jsonify
import os
import _pickle as cPickle
import copy
import sys
sys.path.append('/Users/kevingmagana/DSI/capstone/capstone-update/Capstone_Proposal/py_scripts/')
import results

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


def get_relevant_info(list_of_case_indices, df):
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
	try:

		# Initialize a employee list
		relevant_info = []

		# create a instances for filling up employee list

		for index in list_of_case_indices:
			relevant_info.append()

			empDict = {
				'case_id': index,
				'case_title': df.case_title[index],
				'case_data': df.date[index],
				'case_text': df.case_text[index],
				'case_html': df.html_format[index]
				# 'case_matches': ## if this is MOST relevant part of text:
				# this is a feature coming soon!!!
			}

			relevant_info.append(empDict)

		# convert to json data
		jsonStr = json.dumps(relevant_info)

	except:
		print (str('Nothing here'))

	return jsonify(CourtCases=jsonStr)


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
	query = ''.join(list(dict_results))
	ranked_indices = process_query(query)

	return get_relevant_info(ranked_indices, model[3])##JSON FILE




