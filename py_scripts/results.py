"""
The online legal research engine
"""

from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import sys

import _pickle as cPickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import boto3
from io import StringIO, BytesIO
import numpy as np
from functools import reduce
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import string
from sklearn.metrics.pairwise import linear_kernel
import json



def load_fitted_query_parser(file_path):
    """
    :param file_path: directory pathway, of the fitted query parser
    :returns: Query object
    """
    ## read
    with open(file_path, "rb") as f:
        index_model = cPickle.load(f)
    return index_model


def indexed_results(parser, query):
    """
    :param parser: Query Object
    :param query: String
    :return: Dictionary, of indexed cases that matched the query
            {keys: DocID, Value: Case_Title}
    """
    q= parser
    return q.query(query)


def get_vectors(data):
    """
    :param data: pandas series, all court_cases in corpus
    :return: array of arrays, a matrix of all TF-IDF weights;
            TfidfVectorizer object.
    """
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(data).toarray()
    return vectors, vectorizer

def get_index_vectors(main_tfidf_vector, index_results ):
    """
    :param main_tfidf_vector: array of arrays, of the TF-IDF weights on all corpus
    where the rows are the cases, and the columns are the entire vocabulary.
    :param index_results: dict, of the indexed results where the keys are the
    indices and the values are the cases
        EX:
        {1132: 'Peralta-Taveras v. Gonzales 06/06/2007',
        4457: 'Moncrieffe v. Holder 04/23/2013', ... }

    :return: array of arrays, of just the indexed case TF-IDF weights
        where the rows are the indexed cases, and the colunns are the entire corpus vocabulary
        EX:
        array([
                [0. , 0. , 0.  , ..., 0. , 0. , 0.],
                [0. , 0. , 0.  , ..., 0. , 0. , 0.],
                [0.01239151 , 0. , 0.  , ..., 0. , 0. , 0.],
                [0. , 0. , 0.  , ..., 0. , 0. , 0.],
                [0. , 0. , 0.  , ..., 0. , 0. , 0.] ... ,] )
        IN:  array.shape
        OUT: (127, 81825)

    :return case_index_dict: dict, to keep track of the indexed cases and the
    array values they get.
            EX:
            {key: case array value, value: case_index}
            {1: 1132, 2: 4457, ... }
    """

    array = np.zeros((len(index_results), main_tfidf_vector.shape[1]))
    case_index_dict ={}

    for ind, res in enumerate(index_results):
        array[ind] = main_tfidf_vector[res]
        case_index_dict[ind] = res

    return array, case_index_dict

def query_vector(vect_obj, question ):
    """
    :param main_tfidf_vector: array of arrays, of the TF-IDF weights of entire corpus
    :param stem_words: list, of stemmed words in query.

    :param vect_obj: Tf-IDF object
    :param question: string, the query
    :return: 1-D array, vectorized query
        ## EX:
            IN: array.shape
            OUT: (1, 81833)
    """
    # array = np.zeros((1, main_tfidf_vector.shape[1]))
    #
    # for ind, word in enumerate(stem_words):
    #     feature_names = vect_obj.get_feature_names()
    #     index = feature_names.index(word)
    #     array[index] = 1  ### WHAT SHOULD GO HERE?????
    #                     ### Simple count???
    #                     ### How to vectorize query...
    tokenized_queries = vect_obj.transform(list(question))
    return tokenized_queries

def cosine_similarity(tokenized_query, ind_vectors):
    """
    :param tokenized_query: 1-D array, vector of query for cosine similarity ranking
    :param ind_vectors:
    :return: 1-D array, of cosine similarity scores
    """
    return linear_kernel(tokenized_query, ind_vectors)



def get_top_values(lst, n):
    '''
    INPUT: LIST, INTEGER, LIST
    OUTPUT: LIST

    Given a list of values, find the indices with the highest n values.
    Return the labels for each of these indices.

    e.g.
    lst = [7, 3, 2, 4, 1]
    n = 2
    labels = ["cat", "dog", "mouse", "pig", "rabbit"]
    output: ["cat", "pig"]

    [-1:-n-1:-1]
    '''
    return [i for i in np.argsort(lst)[-1:-n - 1:-1]]


def tokenize(tokenize_query):
    """
    Tokenize: Removes all punctuation
    :param tokenize_query: string, query
    :returns: list of strings, tokenized words
    """
    table = str.maketrans({key: None for key in string.punctuation})
    return word_tokenize(tokenize_query.translate(table).lower())

def remove_stop_words(remove_stop_text):
    """
    :param case_text: list of strings (tokens)
    :returns: list of strings(tokens) without stopwords
    """
    stop = set(stopwords.words('english'))
    return [word for word in remove_stop_text if word not in stop]

def stem_words(stem_word_text):
    """
    :param without_stop: list of strings without stop words
    :return: list of strings (stemmed words)
    """
    snowball = SnowballStemmer('english')
    return [snowball.stem(word) for word in stem_word_text]

def load_data(local= True):
    """
    load_data is a function that will load the csv file from AWS S3 bucket, and will return the
    desired dataframe with the title_date and case_text columns.

    :return: dataframe, with 2 columns: title_date and case_text
    """
    if local:
        # -- LOAD FROM LOCAL MACHINE --
        df = pd.read_csv('/Users/kevingmagana/DSI/capstone/case_corpus.csv')
        df = df.dropna()
        df['title_date'] = df[['case_title', 'date']].apply(lambda x: ' '.join(x), axis=1)


        df2 = df.iloc[:, [2, 12]]
        df2 = df2.drop_duplicates(subset='title_date')
        df2 = df2.reset_index(drop=True)
    else:
        # -- LOAD FROM Amazon Web Services --
        s3 = boto3.resource('s3')
        client = boto3.client('s3')  # low-level functional API

        obj = client.get_object(Bucket='court-case-data', Key='merged_data_with_html_format.csv')
        df = pd.read_csv(BytesIO(obj['Body'].read()))
        df = df.dropna()
        df['title_date'] = df[['case_title', 'date']].apply(lambda x: ' '.join(x), axis=1)

        # df2 = df.iloc[:, [2, 12]]
        df = df.drop_duplicates(subset='title_date')
        df = df.reset_index(drop=True)

        ## df2 is the 2 column df, whereas df is simply all the columns
    return df


def load_model(first_time = True):
    ## df2 is the 2 column df, whereas df is simply all the columns
    if first_time:
        df2, df = load_data(local=True)
        data = df2.case_text
    else:
        try:
            df= pd.read_csv('/Users/kevingmagana/DSI/capstone/case_corpus.csv')
            data = df.case_text
        except:
            df = pd.read_csv('/home/ec2-user/github/dataset.csv')
            data = df.case_text
    # Step 3: Load fitted query parser
    try:
        FILE_PATH = "/Users/kevingmagana/DSI/capstone/fitted_query_parser_updated4.pkl"
        loaded_parser = load_fitted_query_parser(FILE_PATH)
    except:
        FILE_PATH = "/home/ec2-user/github/fitted_query_parser3.pkl"
        loaded_parser = load_fitted_query_parser(FILE_PATH)

    # Step 5: Vectorize corpus
    tf_idf_vectors, vectorizer_obj= get_vectors(data)
    return loaded_parser, vectorizer_obj, tf_idf_vectors, df


# def process_query(query):
#     """
#     :param query: string, the query
#     :return: list, of indices or DOC IDs
#     """
#
#     # Step 1: Intake and get Indexed Cases
#     query =  query
#     indices = results.indexed_results(model[2], query)
#
#     # Step 2: Get index_vectors and case_val dictionary
#     index_vectors, case_value_dictionary= results.get_index_vectors(model[5], indices)
#
#     # Step 3: Vectorize query
#     vectorized_query = results.query_vector(model[3], query)
#
#     # Step 4: Get Cosine similarities
#     cosine_similarities = cosine_similarity(vectorized_query, model[4])
#
#     # Step 5: Get top results and rank them
#     top_results = (get_top_values(cosine_similarities[0], 10), query)
#
#     res = [case_value_dictionary[array_value] for array_value in top_results[0]]
#
#     return res

if __name__ == "__main__":
    from query_parser import Query
    # Step 1: Load Data
    remote = input('On AWS EC2 Instance? (y/n):')
    if remote == 'y':
        df2, df = load_data(local=False)
    else:
        df2, df = load_data(local=True)
        data = df.case_text

        print('What would you like to know about immigration law? ')
        wait = input("")
        print('Examples include: ',
              'What is the penalty for drug trafficking?',
              'What is the deportation process for human traffickers?',
              'Can immigrants seek asylum from Mexico?')
        wait = input("")

        # Step 2: Ask and parse Legal Query/Question
        query  = str(input("Ask Legal Question Related to Immigration: "))
        print('Please Wait ... ')
        # tokenized = tokenize(query)
        # removed_stop_words = remove_stop_words(tokenized)
        # stemmed_words = stem_words(removed_stop_words)

        # Step 3: Load fitted query parser
        FILE_PATH = "/Users/kevingmagana/DSI/capstone/fitted_query_parser_updated4.pkl"
        loaded_parser = load_fitted_query_parser(FILE_PATH)

        # Step 4: Find matched cases with query terms
        indices = indexed_results(loaded_parser, query)
        """ EX: 
            {1132: 'Peralta-Taveras v. Gonzales 06/06/2007', 
            4457: 'Moncrieffe v. Holder 04/23/2013', ... """

        # Step 5: Vectorize corpus and query
        tf_idf_vectors, vectorizer_obj= get_vectors(data)
        index_vectors, case_value_dictionary= get_index_vectors(tf_idf_vectors, indices)
        vectorized_query = query_vector(vectorizer_obj, query)
            ## Potentially pass stemmed_words and tf-idf vectors above

        # Step 6: Rank using cosine similarity
        cosine_similarities = cosine_similarity(vectorized_query, index_vectors)
        top_results = (get_top_values(cosine_similarities[0], 10), query)

        print(top_results[1])
        print([case_value_dictionary[array_value] for array_value in top_results[0]])







