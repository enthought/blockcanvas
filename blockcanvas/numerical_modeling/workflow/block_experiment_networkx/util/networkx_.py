'Extensions to the networkx graph library.'

from networkx import \
    DiGraph, Graph, all_pairs_shortest_path, bfs, is_directed_acyclic_graph

from traits.util.dict import map_items, map_keys
from traits.util.sequence import union

class CyclicGraph(Exception):
    def __init__(self, msg=''):
        msg = str(msg)
        if msg:
            msg = ': ' + msg
        Exception.__init__(self, 'Cyclic graph' + msg)

def closure(g):
    ''' Compute the transitive closure of a graph.

        Undirected:

            >>> g = Graph({1: [2], 2: [3, 4]})
            >>> sorted( g.edges() )
            [(1, 2), (2, 3), (2, 4)]
            >>> sorted( closure(g).edges() )
            [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]

        Directed:

            >>> g = DiGraph({1: [2], 2: [3, 4]})
            >>> sorted( g.edges() )
            [(1, 2), (2, 3), (2, 4)]
            >>> sorted( closure(g).edges() )
            [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
    '''
    return g.__class__(all_pairs_shortest_path(g))

def graph_map(f, graph):
    ''' Maps function f over the nodes in graph.

        >>> sorted( graph_map(str, Graph({1: [2, 3]})).edges() )
        [('1', '2'), ('1', '3')]
        >>> sorted( graph_map(str, DiGraph({1: [2, 3]})).edges() )
        [('1', '2'), ('1', '3')]
    '''
    g = graph
    return g.__class__(map_items(lambda k,v: (f(k), map_keys(f, v)), g.adj))

def reachable_graph(graph, *nodes):
    ''' Return the subgraph of the given graph reachable from the given nodes.

        Assumes 'graph' is directed and acyclic.

        >>> g = DiGraph({1: [2], 2: [3, 4], 5: [6]})

        >>> sorted( reachable_graph(g, 1).nodes() )
        [1, 2, 3, 4]
        >>> sorted( reachable_graph(g, 1).edges() )
        [(1, 2), (2, 3), (2, 4)]

        >>> sorted( reachable_graph(g, 2).nodes() )
        [2, 3, 4]
        >>> sorted( reachable_graph(g, 2).edges() )
        [(2, 3), (2, 4)]

        >>> sorted( reachable_graph(g, 3).nodes() )
        [3]
        >>> sorted( reachable_graph(g, 3).edges() )
        []

        >>> sorted( reachable_graph(g, 4).nodes() )
        [4]
        >>> sorted( reachable_graph(g, 4).edges() )
        []

        >>> sorted( reachable_graph(g, 5).nodes() )
        [5, 6]
        >>> sorted( reachable_graph(g, 5).edges() )
        [(5, 6)]

        >>> sorted( reachable_graph(g, 6).nodes() )
        [6]
        >>> sorted( reachable_graph(g, 6).edges() )
        []
    '''
    assert is_directed_acyclic_graph(graph)

    return graph.subgraph(union( bfs(graph, n) for n in nodes ))
