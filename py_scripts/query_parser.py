import sys

try:
    sys.path.append('/Users/kevingmagana/DSI/capstone/capstone-update/Capstone_Proposal/py_scripts')
except:
    sys.path.append('/home/ec2-user/github/Capstone_Proposal/py_scripts')
import index
import re
import _pickle as cPickle
# import cPickle as pickle
import os
from functools import reduce
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import string

"""
Query parser to break apart queries into tokens and return the INTERSECTION of
the list of court cases that include each token. 
    EX: 
    query = 'What is the penalty for drug trafficking?'
    
    results: 
        {1132: 'Peralta-Taveras v. Gonzales 06/06/2007', 
        2072: 'RENTERIA-GONZALEZ v. IMMIGRATION & NATURALIZATION SERV. 11/11/2002', 
        4457: 'Moncrieffe v. Holder 04/23/2013', 
        3663: 'Ramirez-Altamirano v. Holder 04/14/2009', 
        3915: 'Perez-Enriquez v. Gonzales 09/15/2006', 
        3285: 'US v. Lopez 08/07/2014', 
        695: 'Berhe v. Gonzales 09/26/2006',

"""


class Query:
    def __init__(self, index_object, caseNames, indices, union=False):  # query, union=True):

        self.index = index_object
        self.caseNames = caseNames
        self.union = union  # If False == Intersection
        self.indices = indices
        # indices = {'Porro v. Barnes 11/09/2010': 0, 'Garcia-Carbajal v. Holder 11/05/2010': 1, ...}
        self.invertedIndex = self.index.totalIndex
        # invertedIndex =  {word: {case_title: [pos1, pos2]}, ...}, ...}
        self.regularIndex = self.index.regdex
        # regularIndex = {case_title: {word: [pos1, pos2, ...]}, ...}


    def tokenize(self, tokenize_query):
        """
        Tokenize: Removes all punctuation
        :param tokenize_query: string, query
        :returns: list of strings, tokenized words
        """
        table = str.maketrans({key: None for key in string.punctuation})
        return word_tokenize(tokenize_query.translate(table).lower())

    def remove_stop_words(self, remove_stop_text):
        """
        :param case_text: list of strings (tokens)
        :returns: list of strings(tokens) without stopwords
        """
        stop = set(stopwords.words('english'))
        return [word for word in remove_stop_text if word not in stop]

    def stem_words(self, stem_word_text):
        """
        :param without_stop: list of strings without stop words
        :return: list of strings (stemmed words)
        """
        snowball = SnowballStemmer('english')
        return [snowball.stem(word) for word in stem_word_text]

    def query(self, query, union=False):
        """
        :param query: string, the full query
        :param union: bool, optional. If TRUE: Take UNION of
        list of court cases each word/token is in. If FALSE:
        take INTERSECTION.
        :returns: Dict, where keys are the indexes of the cases,
        and the values are the actual cases themselves.

            EX: {0: 'Porro v. Barnes 11/09/2010',
                 1: 'Garcia-Carbajal v. Holder 11/05/2010', ... }

        """
        if """ " """ in query:
            results = self.phrase_query(query)

        else:
            self.tokenized = self.tokenize(query)
            self.removed_stop_words = self.remove_stop_words(self.tokenized)
            self.stemmed_words = self.stem_words(self.removed_stop_words)

            if len(self.stemmed_words) == 1:
                results = self.one_word_query(self.stemmed_words)
            else:
                results = self.free_text_query(self.stemmed_words)
                #  {'Porro v. Barnes 11/09/2010', 'Garcia-Carbajal v. Holder 11/05/2010', ... }

        index_case_dict = {self.indices[result]: result for result in results}
            # {0: 'Porro v. Barnes 11/09/2010', 1: 'Garcia-Carbajal v. Holder 11/05/2010', ... }

        return index_case_dict

    def one_word_query(self, word):
        """
        self.invertedIndex ==  # {word: {case_title: [pos1, pos2]}, ...}, ...}
        :param word: string, a word/token
        :return: list, of cases where the word/token appears
        """

        if word[0] in self.invertedIndex.keys():
            return [casename for casename in self.invertedIndex[word[0]].keys()]
        else:
            return []

    def free_text_query(self, list_of_strings):
        """
        :param string: a list of strings (tokens)
        :returns: set, the intersection of cases involving tokens
            EX: {'Porro v. Barnes 11/09/2010', 'Garcia-Carbajal v. Holder 11/05/2010', ... }

        """
        result = []
        for word in list_of_strings:
            result.append(self.one_word_query(word))

        # table = str.maketrans({key: None for key in string.punctuation})
        # case.translate(table).upper()
        # result = [[case.translate(table).upper() for case in sublist] for sublist in result]

        # UNION
        if self.union:
            return list(set(result))
        # INTERSECTION
        else:
            return reduce(set.intersection, map(set, result))



            # # *** PHRASE QUERY ***
    #
    # inputs = 'query string', {word: {filename: [pos1, pos2, ...], ...}, ...}
    # inter = {filename: [pos1, pos2]}

    # def phrase_query(self, string):
    #         pattern = re.compile('[\W_]+')
    #         string = pattern.sub(' ',string)
    #
    #         listOfLists, result = [],[]
    #         for word in string.split():
    #             listOfLists.append(self.one_word_query(word))
    #         setted = set(listOfLists[0]).intersection(*listOfLists)
    #         for filename in setted:
    #             temp = []
    #             for word in string.split():
    #                 temp.append(self.invertedIndex[word][filename][:])
    #             for i in range(len(temp)):
    #                 for ind in range(len(temp[i])):
    #                     temp[i][ind] -= i
    #             if set(temp[0]).intersection(*temp):
    #                 result.append(filename)
    #         return self.rankResults(result, string)

if __name__ == "__main__":
    main()
