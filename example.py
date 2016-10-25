#! /usr/bin/env python3

import networkx as nx
import math
from rea import rea as recursive_enumeration_algorithm

simple = {
    'name': "Simple DTMC",
    'edges': [(1, 2, {'prob': 0.5}),
              (1, 3, {'prob': 0.5}),
              (2, 2, {'prob': 0.3}),
              (2, 3, {'prob': 0.5}),
              (2, 4, {'prob': 0.2}),
              (3, 2, {'prob': 0.5}),
              (3, 4, {'prob': 0.1}),
              (3, 5, {'prob': 0.4})],
    'graph_type': 'probability',
    'source': 1,
    'target': 4
}

bsc_small = {
    'name': "Weighted graph used in my B.Sc. thesis",
    'edges': [(0,  1, {'weight': 3}),
              (1,  2, {'weight': 2}),
              (3,  4, {'weight': 5}),
              (4,  5, {'weight': 6}),
              (6,  7, {'weight': 9}),
              (7,  8, {'weight': 2}),
              (0,  3, {'weight': 2}),
              (3,  6, {'weight': 8}),
              (1,  4, {'weight': 5}),
              (4,  7, {'weight': 2}),
              (2,  5, {'weight': 6}),
              (5,  8, {'weight': 3})],
    'graph_type': 'weight',
    'source': 0,
    'target': 8
}

bsc = {
    'name': "Weighted graph used in my B.Sc. thesis",
    'edges': [( 0,  1, {'weight': 3}),
              ( 1,  2, {'weight': 2}),
              ( 3,  4, {'weight': 5}),
              ( 4,  5, {'weight': 6}),
              ( 6,  7, {'weight': 9}),
              ( 7,  8, {'weight': 2}),
              ( 9, 10, {'weight': 4}),
              (10, 11, {'weight': 3}),
              ( 0,  3, {'weight': 2}),
              ( 3,  6, {'weight': 8}),
              ( 6,  9, {'weight': 4}),
              ( 1,  4, {'weight': 5}),
              ( 4,  7, {'weight': 2}),
              ( 7, 10, {'weight': 2}),
              ( 2,  5, {'weight': 6}),
              ( 5,  8, {'weight': 3}),
              ( 8, 11, {'weight': 4})],
    'graph_type': 'weight',
    'source': 0,
    'target': 11
}

eppstein = {
    'name': "Eppstein's weighted example graph",
    'edges': [( 1,  2, {'weight':  2}),
              ( 1,  5, {'weight': 13}),
              ( 2,  3, {'weight': 20}),
              ( 2,  6, {'weight': 27}),
              ( 3,  4, {'weight': 14}),
              ( 3,  7, {'weight': 14}),
              ( 4,  8, {'weight': 15}),
              ( 5,  6, {'weight':  9}),
              ( 5,  9, {'weight': 15}),
              ( 6,  7, {'weight': 10}),
              ( 6, 10, {'weight': 20}),
              ( 7,  8, {'weight': 25}),
              ( 7, 11, {'weight': 12}),
              ( 8, 12, {'weight':  7}),
              ( 9, 10, {'weight': 18}),
              (10, 11, {'weight':  8}),
              (11, 12, {'weight': 11})],
    'graph_type': 'weight',
    'source': 1,
    'target': 12
}


def create_graph(edges, graph_type, **_):
    G = nx.DiGraph()
    G.add_edges_from(edges)
    G.graph['type'] = graph_type

    # transform probabilities (i.e. 0<=p<=1) into weights for path length
    # by taking the logarithm and flipping the sign
    # thus, e.g., a path with probabilities 0.5, 0.7 has length:
    #     ln(0.5)+ln(0.7) == ln(0.5*0.7)
    if G.graph['type'] == 'probability':
        for e in G.edges():
            probability = G[e[0]][e[1]]['prob']
            prob_to_weight = abs(math.log(probability))
            G.add_edge(e[0], e[1], {'weight': prob_to_weight})

    return G


if __name__ == "__main__":

    selected_graph = bsc_small

    G = create_graph(**selected_graph)
    s = selected_graph['source']
    t = selected_graph['target']
    k = 5

    print("Computing the {k} shortest paths from {s} to {t} in graph '{name}' ...".format(k=k, s=s, t=t, name=selected_graph['name']))
    print("(No output will be shown. Please use a debugger to step through the algorithm and inspect the results.)")

    recursive_enumeration_algorithm(G, s, t, k)

    print("Done.")
    print("Just as an example, here's the {k}-th shortest path from {s} to {t}:\n{p}".format(k=k, s=s, t=t, p=G.node[t][k]['path']))
