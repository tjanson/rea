import networkx as nx
import math


def create_graph():
    edges = [(1, 2, 0.5),
             (1, 3, 0.5),
             (2, 2, 0.5),
             (2, 4, 0.5),
             (3, 4, 0.2),
             (3, 5, 0.8)]

    G = nx.DiGraph(name="Graph with probabilities as weights")
    G.add_weighted_edges_from(edges)


    G_log = nx.DiGraph(name="Graph with transformed weights for shortest paths")

    for e in G.edges():
        original_weight = G[e[0]][e[1]]['weight']
        transformed_weight = abs(math.log(original_weight))
        G_log.add_edge(e[0], e[1], {'weight': transformed_weight})

    return G_log


if __name__ == "__main__":
    G = create_graph()