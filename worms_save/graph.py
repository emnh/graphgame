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
        d = 0
        for i in range(len(node.cpos)):
            d += abs(n.cpos[i] - n2.cpos[i])**2
        d = d ** 0.5
        return d

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
            for node in item.nodes:
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
