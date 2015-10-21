# documentation TODO: data structures (esp. tail_k, Path), alg
# TODO: experiment with leaving off the last node (which is implicit)

import networkx as nx
import math


class Path:
    def __init__(self, *, head, tail, tail_k=None, graph):
        self.head = head
        self.tail = tail
        self.tail_k = tail_k
        self.graph = graph

        if tail is None:
            self.length = 0
        else:
            self.length = tail.length + graph[tail.head][head]['weight']
            assert self.length > 0

        self.prob = math.e ** (-self.length)

    def __len__(self):
        return 1 if self.tail is None else 1 + len(self.tail)

    def __str__(self, *, head=True):
        info_str = " [Prob: {:.3f}]".format(self.prob) if head else ""

        if self.tail is None:
            return "Path (tail first): {}".format(self.head) + info_str
        else:
            tail_str = self.tail.__str__(head=False)
            return "{tail} {head}".format(tail=tail_str, head=self.head) + info_str

    def __repr__(self):
        return self.__str__()

    # for hashing and equality, only consider the nodes of the path
    # this is good in case rounding or optional (meta-)data differs on otherwise identical paths
    # (not sure if this will be a bad idea in some edge case - better watch this)
    def __eq__(self, other):
        return self.head == other.head and self.tail == other.tail

    def __hash__(self):
        return hash(tuple(self.to_list()))

    @classmethod
    def from_list(cls, l, *, graph):
        if l is None or l == []:
            raise RuntimeError("Attempted to create Path from empty list")

        if len(l) == 1:
            return cls(head=l[0], tail=None, graph=graph)
        else:
            return cls.from_list(l[:-1], graph=graph).prepend(l[-1])

    def to_list(self):
        tail_list = [] if self.tail is None else self.tail.to_list()
        return [self.head] + tail_list

    def prepend(self, node, *, tail_k=None):
        # NOTE: Maybe it's just too late, but I just confused myself:
        # I've accidentally made the following convention (which is good
        # for implementation, but somewhat unintuitive):
        #
        # A path following directed edges from 1 to 4 is represented as:
        #     1 -> 2 -> 3 -> 4
        #     [ tail    ]    [head]
        #
        # Nodes are `prepend`ed at the head (so far, so good, right?),
        # but that's really the "end" of the path.
        # So, maybe I should rename it to `append`, but that would be
        # confusing too ...
        # DOC-FIXME
        p = Path(head=node, tail=self, tail_k=tail_k, graph=self.graph)
        assert p.length > 0
        return p


def create_graph():
    edges = [(1, 2, {'prob': 0.5}),
             (1, 3, {'prob': 0.5}),
             (2, 2, {'prob': 0.3}),
             (2, 3, {'prob': 0.5}),
             (2, 4, {'prob': 0.2}),
             (3, 2, {'prob': 0.5}),
             (3, 4, {'prob': 0.1}),
             (3, 5, {'prob': 0.4})]

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
        raw_shortest_path = nx.dijkstra_path(G, source, v)
        shortest_path = Path.from_list(raw_shortest_path, graph=G)
        shortest_path.tail_k = 1

        G.node[v][1] = {'path': shortest_path}


def rea(G, source, target, k):
    """Recursive Enumeration Algorithm (Jimenez & Marzal)

       Computes the `k` shortest paths from `source` to `target`
       in graph `G`."""

    def compute_next_path(v, iteration):
        # FIXME: this will work, but is it necessary? I should find out
        assert iteration not in G.node[v]
        G.node[v][iteration] = {}
        G.node[v][iteration]['candidates'] = set()

        if iteration == 2:
            shortest_path_to_v = G.node[v][1]['path']

            shortest_paths_to_pred_plus_edge_to_v = \
                {G.node[u][1]['path'].prepend(v, tail_k=1) for u in G.predecessors(v)}
            candidates = shortest_paths_to_pred_plus_edge_to_v - {shortest_path_to_v}

            G.node[v][2]['candidates'].update(candidates)

        if iteration != 2 or v != source:
            # consider the previous iteration's path to current node `v`, and
            # specifically the last node (before `v`) in that path
            prev_pred = G.node[v][iteration - 1]['path'].tail.head

            # the path to that `prev_pred` is the `k`-th best path to that
            # node for some `k`
            tail_k = G.node[v][iteration - 1]['path'].tail_k

            if tail_k + 1 not in G.node[prev_pred]:
                # `tail_k + 1`-th best path to `prev_pred` has not yet been computed
                compute_next_path(prev_pred, tail_k + 1)

            # the result of that (plus an edge to `v`) is a candidate path
            if 'path' in G.node[prev_pred][tail_k + 1]:
                # else there was no path (no candidates)
                path = G.node[prev_pred][tail_k + 1]['path'].prepend(v, tail_k=tail_k + 1)
                G.node[v][iteration]['candidates'].add(path)

        if len(G.node[v][iteration]['candidates']):
            min_length_candidate = min(G.node[v][iteration]['candidates'], key=lambda p: p.length)
            G.node[v][iteration]['candidates'].remove(min_length_candidate)
            G.node[v][iteration]['path'] = min_length_candidate
        else:
            # TODO: check how to handle this case
            #raise RuntimeError("Path does not exist (k={}, v={})".format(iteration, v))
            # maybe just don't do anything??
            pass

    initialize_rea(G, source)

    for i in range(2, k + 1):
        compute_next_path(target, i)


if __name__ == "__main__":

    G = create_graph()
    s = 1
    t = 4
    k = 5

    rea(G, s, t, k)

    print("Done.")
