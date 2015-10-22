import math


class Path:
    # TODO: document, especially `tail_k`
    #
    # A path following directed edges from 1 to 4 is represented as a
    # head (node 4) and a pointer to (the head of) a path from 1 to 3:
    #     Path: 1 -> 2 -> 3 -> 4
    #     Repr: [ tail    ] <- [head]

    def __init__(self, *, head, tail, tail_k=None, graph):
        self.head = head
        self.tail = tail
        self.tail_k = tail_k
        self.graph = graph
        self._hash = None

        if tail is None:
            self.length = 0
        else:
            self.length = tail.length + self.graph[tail.head][head]['weight']

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

    # TODO: find out if there is a less expensive way for comparison & especially hashing
    # this is almost certainly a pretty bad hash function, but it doesn't seem to matter much
    def __hash__(self):
        some_large_number = 541

        if self._hash is None:
            if self.tail is None:
                self._hash = self.head % some_large_number
            else:
                self._hash = int(str(self.head) + str(hash(self.tail))) % some_large_number
        return self._hash

    @classmethod
    def from_list(cls, l, *, graph):
        if l is None or l == []:
            raise RuntimeError("Attempted to create Path from empty list")

        if len(l) == 1:
            return cls(head=l[0], tail=None, graph=graph)
        else:
            return cls.from_list(l[:-1], graph=graph).append(l[-1])

    def to_list(self):
        tail_list = [] if self.tail is None else self.tail.to_list()
        return [self.head] + tail_list

    def append(self, node, *, tail_k=None):
        return Path(head=node, tail=self, tail_k=tail_k, graph=self.graph)
