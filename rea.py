import networkx as nx
import math
from collections import namedtuple


class Path(namedtuple('Path', ['head', 'tail', 'length'])):
    @staticmethod
    def from_list(l, *, graph):
        if l is None or l == []:
            raise RuntimeError("Attempted to create Path from empty list")

        if len(l) == 1:
            return Path(head=l[0], tail=None, length=0)
        else:
            return Path.from_list(l[:-1], graph=graph).prepend(l[-1], graph=graph)

    def prepend(self, node, *, graph):
        edge_length = graph[self.head][node]['weight']
        return Path(head=node, tail=self, length=self.length + edge_length)

    def __len__(self):
        return 1 if self.tail is None else 1 + len(self.tail)

    def __str__(self):
        if self.tail is None:
            return "Path: {}".format(self.head)
        else:
            return "{tail} {head}".format(tail=self.tail, head=self.head)

    def __repr__(self):
        return self.__str__()

#   def __getitem__(self, item):
#       # DEBUG
#       as_list = self._to_list()
#       element = as_list[item]
#       return element

    def _to_list(self):
        tail_list = [] if self.tail is None else self.tail._to_list()
        return [self.head] + tail_list

    def __eq__(self, other):
        # ignore length, in case there's a rounding error or something
        # alternatively, could've used
        return self.head == other.head and self.tail == other.tail

    def __hash__(self):
        return hash(tuple(self._to_list()))


def create_graph():
    edges = [(1, 2, {'prob': 0.5}),
             (1, 3, {'prob': 0.5}),
             (2, 2, {'prob': 0.5}),
             (2, 4, {'prob': 0.5}),
             (3, 4, {'prob': 0.2}),
             (3, 5, {'prob': 0.8})]

    G = nx.DiGraph(name="Graph with probabilities and corresponding weights")
    G.add_edges_from(edges)

    # transform probabilities (i.e. 0<=p<=1) into weights for path length
    # by taking the logarithm and flipping the sign
    # thus, e.g., a path with probabilities 0.5, 0.7 has length:
    #     ln(0.5)+ln(0.7) == ln(0.5*0.7)

    for e in G.edges():
        probability = G[e[0]][e[1]]['prob']
        prob_to_weight = abs(math.log(probability))
        G.add_edge(e[0], e[1], {'weight': prob_to_weight})

    return G


def initialize_rea(G, source):
    """Uses Dijkstra to computes the one-to-all shortest paths from
       `source`.
       That path and its length is stored in the nodes, specifically
       under a key corresponding to the iteration index ('k') starting
       with 1 (sic! i.e., human numbering, same as in the paper)."""
    for v in G.nodes_iter():
        distance = nx.dijkstra_path_length(G, source, v)
        raw_shortest_path = nx.dijkstra_path(G, source, v)
        shortest_path = Path.from_list(raw_shortest_path, graph=G)

        # DEBUG
        distance_as_probability = round(math.e ** -distance, 2)
        print("Distance from {} to {}: -{:.3f} => {:.3f}".format(source, v, distance, distance_as_probability))

        G.node[v][1] = {'length': distance, 'path': shortest_path}


def rea(G, source, target, k):
    """Recursive Enumeration Algorithm (Jimenez & Marzal)

       Computes the `k` shortest paths from `source` to `target`
       in graph `G`."""

    def compute_next_path(v, iteration):
        if iteration == 2:

            shortest_path_to_v = G.node[v][1]['path']
            shortest_paths_to_pred_plus_edge_to_v = {G.node[u][1]['path'].prepend(v, graph=G) for u in G.predecessors(v)}
            candidates = shortest_paths_to_pred_plus_edge_to_v.remove(shortest_path_to_v)

            # more readable (?) version:
            #candidates = set()

            #for u in G.predecessors(v):
            #    candidate_path = G.node[u][1]['path'].prepend(v, graph=G)

            #    if candidate_path != shortest_path_to_v:
            #        candidates.add(candidate_path)

            G.node[v][2] = {'candidates': candidates}

        if iteration != 2 or v != source:
            raise NotImplementedError  # TODO

        if len(G.node[v][iteration]['candidates']):
            raise NotImplementedError  # TODO
        else:
            raise RuntimeError("Path does not exist (k={}, v={})".format(iteration, v))

    initialize_rea(G, source)

    for i in range(2, k + 1):
        compute_next_path(target, i)


if __name__ == "__main__":
    G = create_graph()
    s = 1
    t = 4
    k = 2

    rea(G, s, t, k)

    print("Done.")
