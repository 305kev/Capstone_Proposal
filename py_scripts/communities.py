import networkx as nx
from collections import Counter


def girvan_newman_step(G):
    """Run one step of the Girvan-Newman community detection algorithm.
    Afterwards, the graph will have one more connected component.
    Parameters
    ----------
    G: networkx Graph object
    Returns
    -------
    None
    """
    init_ncomp = nx.number_connected_components(G)
    ncomp = init_ncomp
    while ncomp == init_ncomp:
        bw = Counter(nx.edge_betweenness_centrality(G))
        a, b = bw.most_common(1)[0][0]
        G.remove_edge(a, b)
        ncomp = nx.number_connected_components(G)


def find_communities_n(G, n):
    """Return communites of G after running Girvan-Newman algorithm n steps.
    Parameters
    ----------
    G: networkx Graph object
    n: int
    Returns
    -------
    list of lists
    """
    G1 = G.copy()
    for i in range(n):
        girvan_newman_step(G1)
    return list(nx.connected_components(G1))


def find_communities_modularity(G, max_iter=None):
    """Return communities with the maximum modulairty from G.
    Run Girvan-Newman algorithm on G and find communities with max modularity.
    Parameters
    ----------
    G: networkx Graph object
    max_iter: int, (optional, default=None)
        Maximum number of iterations
    Returns
    -------
    list of lists of strings
        Strings are node names
    """
    degrees = G.degree()
    num_edges = G.number_of_edges()
    G1 = G.copy()
    best_modularity = -1.0
    best_comps = nx.connected_components(G1)
    i = 0
    while G1.number_of_edges() > 0:
        subgraphs = nx.connected_component_subgraphs(G1)
        modularity = get_modularity(subgraphs, degrees, num_edges)
        if modularity > best_modularity:
            best_modularity = modularity
            best_comps = list(nx.connected_components(G1))
        girvan_newman_step(G1)
        i += 1
        if max_iter or i >= max_iter:
            break
    return best_comps


def get_modularity(subgraphs, degrees, num_edges):
    """Return the value of the modularity for the graph G.
    Parameters
    ----------
    subgraphs: generator
        Graph broken in subgraphs
    degrees: dictionary
        Node: degree key-value pairs from original graph
    num_edges: float
        Number of edges in original graph
    Returns
    -------
    float
        Modularity value, between -0.5 and 1
    """
    mod = 0
    for g in subgraphs:
        for node1 in g:
            for node2 in g:
                mod += int(g.has_edge(node1, node2))
                mod -= degrees[node1] * degrees[node2] / (2. * num_edges)
    return mod / (2. * num_edges)


if __name__ == '__main__':
    karateG = nx.karate_club_graph()
    c = find_communities_modularity(karateG)
    print ("Optimal number of communities: {}".format(len(c)))