import pandas as pd
import numpy as np
import find_citation
import networkx as nx
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from collections import defaultdict
import copy
import sys
import re

"""
This pipeline is used to build out the graphs necessary to discover communities.
Main focus is to graph court case documents as nodes and the shared citations between 
cases as the weighted edges. 

To Run: 
    (1) Get data and pass into get_total_corpus_citations() function to return list of citations 
    (2) Then pass in the data and list of citation into the get_graph_dict() function
        to return the graph dictionary 

"""


def _get_citation(citation):
    """
    :param citation: string, a full citation
    :returns: string, a partial citation to serve as the nodes

    EX:
        Baker v. McCollan (1979)
        Graham v. Connor (1989)
        Austin v. Hamilton (1991)

    """
    cite = []
    for ind, word in enumerate(citation.split(' ')):
        if ind == 0 or ind == 1 or ind == 2:
            cite.append(word.strip(','))
        try:
            s = re.search(r"\d+(\.\d+)?", word)
            year = int(s.group(0))
            if year > 1750 and year <= 2018 and ind > (len(citation.split(' '))) * .80:
                year = "(", str(year), ")"
                year = "".join(year)
                cite.append(year)
        except:
            continue
    return " ".join(cite)


def _get_all_citations(document):
    """
    :param document: string, legal document with citations
    :returns: list, a list of all citations within the document

    """
    citations_objects = find_citation.get_citations(document, html=False)
    citations_strings = []

    for obj in citations_objects:
        citations_strings.append(str(obj))

    results = []
    for citation in citations_strings:
        results.append(_get_citation(citation))
    return results


def get_total_corpus_citations(data):
    """
    :param data: pandas series, all court document texts
    :return: list of lists, list of all document citation lists
    """
    return [_get_all_citations(document) for document in data]


def final_list_of_citations(all_citations):
    """
    :param all_citations: list of lists, each list has all the citations per document
    :returns: list of lists, updated lists: replaced "States" as plaintiff with "United States"

    EX:
        all_citations= "States v. Brown (2008)"
        returns = "United States v. Brown (2008)"
    """
    replace_words = {"states"}
    for first, lst in enumerate(all_citations):
        for second, citation in enumerate(lst):
            cite = citation.split(' ')[0]
            if cite.lower() in replace_words:
                all_citations[first][second] = citation.replace(cite, "United States")

    # Updated Citations
    return all_citations


def get_case_titles(court_case):
    """
    :param court case: STRING, court case document
    :returns: STRING, case title
        EX:
        'UNITED STATES v. RENDON-ALAMO (2010)'
    """
    case_title = []
    for ind, line in enumerate(court_case.splitlines()[0:5]):
        if ind == 1:
            for word in line.split(' '):
                if word.isupper() or word == 'v.':
                    case_title.append(word.strip(','))
        if ind == 3:
            year = "(", line[-4:], ")"
            year = "".join(year)
            case_title.append(year)
    return " ".join(case_title)

def get_graph_dict(data, all_citations):
    """
    :param data: Pandas series, all the court case texts
    :param all_citations: list of lists, all the corpus citations
    :return: dict, key: court case, value: List of citations

    """
    graph_dict = {}
    fixed_citations = final_list_of_citations(all_citations)
    for ind, document in enumerate(data):
        graph_dict[get_case_titles(document)] = fixed_citations[ind]
    return graph_dict


if __name__ == "__main__":
    df = pd.read_csv('/Users/kevingmagana/DSI/capstone/external_data/first_merged_case_law.csv', sep='\t',
                     encoding='utf-8')
    data = df.case_text[df.case_text.notnull()]
    all_citations = get_total_corpus_citations(data)
    graph_dict = get_graph_dict(data, all_citations)

    count=0
    for key, value in graph_dict.items():
        count += 1
        if count > 5:
            break
        print(key.replace(';', '')), print(value)





