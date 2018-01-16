"""
A set of functions that will process that data for training and prediction.
"""

import pandas as pd


def load_data(filename):
    """
    Load the data in json format.
    :param filename: str, the relative path to a json file
    :return: df, a pandas dataframe of the json file
    """
    return pd.read_json(filename)


class DataProcessing:
    """
    A class that will handle all data preprocessing
    """
    def __init__(self, train, df):



        pass




