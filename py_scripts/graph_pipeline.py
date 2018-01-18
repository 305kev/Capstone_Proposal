import pandas as pd
import numpy as np
import sys
try:
    sys.path.append('/Users/kevingmagana/DSI/capstone/capstone-update/Capstone_Proposal/py_scripts')
except:
    sys.path.append('/home/ec2-user/github/Capstone_Proposal/py_scripts')

import find_citation
import networkx as nx
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from collections import defaultdict
import copy
import sys
import re
import community



"""
This pipeline is used to build out the graphs necessary to discover communities.
Main focus is to graph court case documents as nodes and the shared citations between 
cases as the weighted edges. 


"""


class GraphRecommender:
    def __init__(self, dataframe, nx_graph_obj):
        self.df = dataframe
        self.case_text = self.df.case_text
        self.title_date = self.df.title_date

        self.all_citations = self.get_total_corpus_citations(self.case_text)

        self.g = nx_graph_obj
        self.graph_dict = self.get_graph_dict(self.df, self.all_citations)
        self.weighted_edge_graph = self.build_weighted_edge_graph()
        # self.g and the weighted egde graph will become the same.
        # just instantiated here to create the weighted edge graph

        ## Build Community/Node Dicts from graph
        self.parts, self.check = self.build_node_community_dicts(self.g)
        ## self.parts = {Node: Community}
        # EX: how to run search of community number:
        """
        gr = GraphRecommender()
        search_query='Carpio v. Holder 01/13/2010'
        community_value = gr.parts[search_query]
        print(community_value)
        """
        ## self.check = {Community: Nodes}
        # EX: how to look up cases inside a community
        """
        commuity_nodes = gr.check[community_value]
        print(len(commuity_nodes))
        print(commuity_nodes)        
        """

    def _get_citation(self, citation):
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

    def _get_all_citations(self, document):
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
            results.append(self._get_citation(citation))
        return results

    def get_total_corpus_citations(self, data):
        """
        :param data: pandas series, all court document texts
        :return: list of lists, list of all document citation lists
        """
        return [self._get_all_citations(document) for document in data]

    def final_list_of_citations(self, all_citations):
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

    def get_graph_dict(self, case_data, all_citations):
        """
        :param data: Pandas series, all the court case texts
        :param all_citations: list of lists, all the corpus citations
        :return: dict, key: court case, value: List of citations
        """
        graph_dict = {}
        fixed_citations = self.final_list_of_citations(all_citations)
        for ind, document in enumerate(case_data.case_text):
            graph_dict[case_data.title_date[ind]] = fixed_citations[ind]
        return graph_dict

    def _get_weights(self, list_a, list_b):
        """
        :param list_a: string, first node
        :param list_b: string, next node
        :returns: int, weights
        """
        return len(set(list_a) & set(list_b))

    def build_weighted_edge_graph(self):
        """
        This function is to create a weighted edge graph made of
        court cases (nodes) connected by shared citations (edge weights)
        to be used to identify communities, and make recommendations
        of similar cases per search result.
        :returns: None
        """
        for ind, (key, value) in enumerate(self.graph_dict.items()):
            self.g.add_node(key)
            list_a = self.graph_dict[key]
            for inx, (other_nodes, other_values) in enumerate(self.graph_dict.items(), ind + 1):
                list_b = self.graph_dict[other_nodes]
                if list_a == list_b:
                    continue
                else:
                    weight = self._get_weights(list_a, list_b)
                    self.g.add_edge(key, other_nodes, weight=weight)
        return self.g

    def build_node_community_dicts(self, g):
        """
        :param g: networkx graph object
        :returns parts: dict, {Node: Community};
                check: dict, {Community: Node}
        """
        # parts = {Node: Community}
        parts = community.best_partition(g, weight='weight')
        # check = {Community: Node}
        check = {}
        for key, value in parts.items():
            if value not in check:
                check[value] = [key]
            else:
                check[value].append(key)
        return parts, check

    def get_recommendations(self, node_query, commuity_nodes, weights=False, top_n=5):
        """
        :param G: a fitted network graph object
        :param node_query: string, used to locate a community.
        :param community_nodes: list of strings, of title_dates
        :returns: a list, of ranked recommendations
        """
        H = self.g.subgraph(commuity_nodes)
        edges = H.edges(data=True)

        ## list of 3-tuples; where 3rd item is dictionary {'weight': value}
        node_community = [tup for tup in edges if node_query in tup]
        sort = sorted(node_community, key=lambda x: x[2]['weight'])[::-1][:top_n]
        weighted_results_list = defaultdict(None)
        for tup in sort:
            for item in tup:
                if node_query not in item and type(item) != dict:
                    weighted_results_list[item] = None
                elif type(item) == dict:
                    weighted_results_list[tup[1]] = item
                else:
                    continue
        if weights:
            results = {key: value['weight'] for key, value in weighted_results_list.items()}
        else:
            results = [res for res in weighted_results_list.keys()]
        return results
