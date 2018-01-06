"""
The online prediction engine
"""

from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import sys
sys.path.append('/Users/kevingmagana/DSI/capstone/capstone/py_scripts')
from data_processing import DataProcessing
import json




DATAFRAME = pd.read_csv('../data/src_law/first_merged_case_law.csv', sep='\t', encoding='utf-8')

def results(search_query, ready=False):
    """
    Uses a model to return the top k most relevant documents
    :param model: object, a trained SK-Learn style model object
    :param to_predict: string, raw string query
    :return: dictionary of dictionaries
    """

    if ready:
        return "Not yet!"

    else:
        case_court =  DATAFRAME.court[0]
        case_title = DATAFRAME.case_title[0]
        case_text = DATAFRAME.case_text[0]
        case_date = DATAFRAME.date[0]
        case_tags= DATAFRAME.tags[0]

        return [{'case_title': case_title}, {'case_date': case_date}, {'case_text': case_text}]


if __name__ == "__main__":


    # model= None
    search_query = "What is a good first query?"
    title, date, text = results(search_query)

    print(title)
    print(date)
    print(text)
