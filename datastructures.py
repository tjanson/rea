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
            self.length = tail.length + self.graph[tail.head][head]['weight']
            assert self.length > 0

    def __len__(self):
        return 1 if self.tail is None else 1 + len(self.tail)

    def __str__(self, *, head=True):
        if head:
            if self.graph.graph['type'] == 'probability':
                probability = math.e ** (-self.length)
                prefix = "Path [Prob: {:.3f}]: ".format(probability)
            else:
                prefix = "Path [Dist: {:.2f}]: ".format(self.length)
            return prefix + '"' + self.__str__(head=False) + '"'

        if self.tail is None:
            return "{}".format(self.head)
        else:
            tail_str = self.tail.__str__(head=False)
            tail_k_str = " [{}] ".format(self.tail_k) if self.tail_k is not None else " "
            return "{tail}{tail_k}{head}".format(tail=tail_str, tail_k=tail_k_str, head=self.head)

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

