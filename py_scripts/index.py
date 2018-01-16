

#input = [file1, file2, ...]
#res = {filename: [world1, word2]}

import re
import math
import pandas as pd
import numpy as np
import sys
sys.path.append('/Users/kevingmagana/DSI/capstone/capstone-update/Capstone_Proposal/py_scripts/')
import find_citation
import networkx as nx
import pandas as pd
from collections import Counter
from collections import defaultdict
import copy
import re
import boto3
from io import StringIO, BytesIO
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from gensim.models import phrases
from gensim.models.phrases import Phraser


"""

This index will serve as the storage place for all the words/tokens in the
corpus, where each word/token will be matched with a list of all the documents
it appears in.

To handle phrases in queries, each key will be the word/token, and each value
will be a dictionary with the key as the document it appears in, and the value
will be the position the word appears in the document.
    -- This will allow the order of the words to be picked up; ex: Stanford University,
    or The Texas State Capitol.

Example of what FULL index looks like:
    {{word: {case_title: [pos1, pos2]}, ...}, ...},
     {word: {case_title: [pos1, pos2]}, ...}, ...},
     {word: {case_title: [pos1, pos2]}, ...}, ...}, ... }

"""


class BuildIndex:

    def __init__(self, cases):
        """
        :param cases: dataframe, with all the data 
    
        """""
        self.tf = {}
        self.df = {}
        self.idf = {}
        self.cases = cases
        self.case_titles = self.cases['title_date']
        self.tokenized = self.tokenize(self.cases['case_text'])
        self.removed_stop_words = self.remove_stop_words(self.tokenized)
        self.stemmed_words = self.stem_words(self.removed_stop_words)

        self.case_to_terms = self.process_cases()

        self.regdex = self.regIndex()
              # Regular index. EX:
              # res = {case_title: {word: [pos1, pos2, ...]}, ...}
        self.totalIndex = self.execute()
             # {word: {case_title: [pos1, pos2]}, ...}, ...}

        # self.vectors = self.vectorize()
        # self.mags = self.magnitudes(self.case_titles)
        # self.populateScores()



    def tokenize(self, tokenize_texts):
        """
        :param case_text: list of strings (case_texts)
        :returns: list of strings, tokenized word.
        """
        table = str.maketrans({key: None for key in string.punctuation})
        return [word_tokenize(case.translate(table).lower()) for case in tokenize_texts]

    def remove_stop_words(self, remove_stop_text):
        """
        :param case_text: list of lists of strings (tokens)
        :returns: list of lists of strings(tokens) without stopwords
        """
        stop = set(stopwords.words('english'))
        return [[word for word in words if word not in stop] for words in remove_stop_text]

    def stem_words(self, stem_word_text):
        """
        :param without_stop: list of lists without stop words
        :return: list of lists of strings (stemmed words)
        """
        snowball = SnowballStemmer('english')
        return [[snowball.stem(word) for word in words] for words in stem_word_text]


    def process_cases(self):
        """
        :param cases: dataframe, colum1=case_titles, column2=case_texts
        :returns case_to_terms: dict, keys: case_titles, values: words/
        tokens in case
            EX:
                case_to_terms = {case_title: [world1, word2], ...}
        """
        case_to_terms = {}
        for ind, case in enumerate(self.case_titles):
            case_to_terms[case] = self.stemmed_words[ind]
        return case_to_terms


    def index_one_case(self, termlist):
        """
        :param termlist: list, list of all terms/tokens in one case
        :returns:  dict, a dictionary of all the terms/tokens as keys, and their
        indexed positions as values.
            EX:
                  #input = [word1, word2, ...]
                    #output = {word1: [pos1, pos2], word2: [pos2, pos434], ...}
        """
        caseIndex = {}
        for index, word in enumerate(termlist):
            if word in caseIndex.keys():
                caseIndex[word].append(index)
            else:
                caseIndex[word] = [index]
        return caseIndex

    def make_indices(self, termlists):
        """
        :param termlists: dict, keys: cases, values: list of words/tokens per case
        :return:  dict, keys: cases, values: dict of key: words, values: list of indexed positions
            #input = {case_title: [word1, word2, ...], ...}
            #res = {case_title: {word: [pos1, pos2, ...]}, ...}
        """
        total = {}
        for caseName in termlists.keys():
            total[caseName] = self.index_one_case(termlists[caseName])
        return total


    def fullIndex(self):
        """
        :return: dict, keys are the words/tokens and the values are the the dict of
        	the case titles
				 #input = {case_title: {word: [pos1, pos2, ...], ... }}
				 #res = {word: {case_title: [pos1, pos2]}, ...}, ...}

        """
        total_index = {}
        indie_indices = self.regdex # {case_title: {word: [pos1, pos2, ...]}, ...}

        for caseName in indie_indices.keys():
            # self.tf[caseName] = {}
            for word in indie_indices[caseName].keys():
                # self.tf[caseName][word] = len(indie_indices[caseName][word])
                # if word in self.df.keys():
                #     self.df[word] += 1
                # else:
                #     self.df[word] = 1
                if word in total_index.keys():
                    if caseName in total_index[word].keys():
                        total_index[word][caseName].append(indie_indices[caseName][word][:])
                    else:
                        total_index[word][caseName] = indie_indices[caseName][word]
                else:
                    total_index[word] = {caseName: indie_indices[caseName][word]}
        return total_index

    def execute(self):
        return self.fullIndex()

    def regIndex(self):
        return self.make_indices(self.case_to_terms)

    def getUniques(self):
        return self.totalIndex.keys()

            #
    # def vectorize(self):
    #     """
    #     :return: dict, keys are all the case_titles, and values is a list of the number of times each
    #     word appears in each document --
    #     	EX:
    #     		{Doc1: [11, 12, 1, 5, 6],
    #     		 Doc2: [12, 11, 1, 4, 12], ... }
    #
    #     """
    #     vectors = {}
    #     for caseName in self.case_titles:
    #         vectors[caseName] = [len(self.regdex[caseName][word]) for word in self.regdex[caseName].keys()]
    #     return vectors
    #
    #
    # def document_frequency(self, term):
    #     """
    #     :param term:
    #     :return:
    #     """
    #     if term in self.totalIndex.keys():
    #         return len(self.totalIndex[term].keys())
    #     else:
    #         return 0
    #
    # def collection_size(self):
    #     return len(self.case_titles)
    #
    # def magnitudes(self, documents):
    #
    #     mags = {}
    #     for document in documents:
    #         mags[document] = pow(sum(map(lambda x: x**2, self.vectors[document])),.5)
    #     return mags
    #
    # def term_frequency(self, term, document):
    #     return self.tf[document][term]/self.mags[document] if term in self.tf[document].keys() else 0
    #
    # def populateScores(self): #pretty sure that this is wrong and makes little sense.
    #     for caseName in self.case_titles:
    #         for term in self.getUniques():
    #             self.tf[caseName][term] = self.term_frequency(term, caseName)
    #             if term in self.df.keys():
    #                 self.idf[term] = self.idf_func(self.collection_size(), self.df[term])
    #             else:
    #                 self.idf[term] = 0
    #     return self.df, self.tf, self.idf
    #
    # def idf_func(self, N, N_t):
    #     if N_t != 0:
    #         return math.log(N/N_t)
    #     else:
    #         return 0
    #
    # def generateScore(self, term, document):
    #     return self.tf[document][term] * self.idf[term]


if __name__ == "__main__":
    df = pd.read_csv('/Users/kevingmagana/DSI/capstone/external_data/first_merged_case_law.csv', sep='\t',
                     encoding='utf-8')
    build_index = BuildIndex(df)
