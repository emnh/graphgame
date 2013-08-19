#!/usr/bin/env python

class Edge(object):
    def __init__(self, node, node2, name=''):
        self.nodes = [node, node2]
        self.name = name

    def other(self, node):
        for x in self.nodes:
            if x != node: return x

    def dist(self):
        n, n2 = self.nodes
        d = sum((n2.cpos - n1.cpos)**2)**0.5
        return d

class DirectedEdge(Edge):
    pass

class Node(object):

    def __init__(self, name):
        self.name = name
        self.edges = []
    
    def add(self, edge):
        self.edges.append(edge)

class Graph(object):

    def __init__(self):
        self.nodes = []
        self.edges = []

    def add(self, item):
        if isinstance(item, Node):
            self.nodes.append(item)
        elif isinstance(item, Edge):
            if isinstance(item, DirectedEdge):
                addtonodes = [item.nodes[0]]
            else:
                addtonodes = item.nodes
            for node in addtonodes:
                node.add(item)
            self.edges.append(item)

    def remove(self, item):
        if isinstance(item, Node):
            n = item
            self.nodes.remove(n)
            for e in reversed(self.edges):
                if n in e.nodes:
                    self.edges.remove(e)
        else:
            raise


if __name__ == "__main__":
    G = Graph()
    n = node
    dup = Node(n.name + "-dup")
    G.add(dup)

    i = 1
    edge = Edge(dup, n, i)
    G.add(edge)
    for i in range(2, 3):
        for dupedge in dup.edges:
            if dupedge.name != i: continue
            other = dupedge.other(dup)
            for otheredge in other:
                other2 = otheredge.other(other)
                edge = Edge(dup, other2, i)
                G.add(edge)
