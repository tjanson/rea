import networkx as nx
from datastructures import Path


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
        G.node[v]['candidates'] = set()


def rea(G, source, target, k):
    """Recursive Enumeration Algorithm (Jimenez & Marzal)

       Computes the `k` shortest paths from `source` to `target`
       in graph `G`."""

    def compute_next_path(v, iteration):
        # FIXME: this will work, but is it necessary? I should find out
        assert iteration not in G.node[v]
        G.node[v][iteration] = {}

        if iteration == 2:
            shortest_path_to_v = G.node[v][1]['path']

            shortest_paths_to_pred_plus_edge_to_v = \
                {G.node[u][1]['path'].append(v, tail_k=1) for u in G.predecessors(v)}
            candidates = shortest_paths_to_pred_plus_edge_to_v - {shortest_path_to_v}

            G.node[v]['candidates'].update(candidates)

        if iteration != 2 or v != source:
            if 'path' not in G.node[v][iteration - 1]:
                # uhh... should this ever happen?
                # let's make it an exception
                raise RuntimeError("No path to {} in previous iteration {}, skipping.".format(v, iteration - 1))

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
            # (if it exists -- else there was no path (no candidates))
            if 'path' in G.node[prev_pred][tail_k + 1]:
                path = G.node[prev_pred][tail_k + 1]['path'].append(v, tail_k=tail_k + 1)
                G.node[v]['candidates'].add(path)

        if len(G.node[v]['candidates']):
            min_length_candidate = min(G.node[v]['candidates'], key=lambda p: p.length)
            G.node[v]['candidates'].remove(min_length_candidate)
            G.node[v][iteration]['path'] = min_length_candidate
        else:
            # TODO: check how to handle this case
            # maybe just don't do anything? - yes, that works
            pass

    initialize_rea(G, source)

    for i in range(2, k + 1):
        compute_next_path(target, i)

