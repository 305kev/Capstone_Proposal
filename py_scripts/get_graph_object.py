

import pandas as pd

"""
This script is to load in a network graph object, fit it with relevant
case data, create a node/community dictionary, and pickle the fitted 
networkx model. 

Intended use is for an AWS EC2 instance. 

"""



if __name__ == "__main__":
    from graph_pipeline import GraphRecommender
    import networkx as nx
    import pandas as pd
    import _pickle as cPickle

    df = pd.read_csv('/home/ec2-user/github/dataset.csv')
    G = nx.Graph()
    gr = GraphRecommender(df, G)

    with open("/home/ec2-user/github/fitted_graph.pkl", "wb") as f:
        cPickle.dump(gr, f)

