"""
Isograph exporter Reliability Block Diagram (RBD) module.

Isograph system modelling is based in reliability block diagrams.
Therefore, the RBD is the core component of an Isograph model.
"""

import logging
import networkx as nx
import pydotplus

from collections import OrderedDict
from sliding_window import window

_logger = logging.getLogger(__name__)

# RBD elements ################################################################

GRAPH_ATTRIBUTES = dict(
    graph=dict(rankdir='LR'), )


class _CompoundBlock(object):
    """
    Class modelling an RBD block.
    """

    def __init__(self, name):
        self._name = name
        self._block_graph = None

    def generate_internal_graph(self, spec_graph, failures_graph):
        g = spec_graph
        f = failures_graph

        def enumerate_blocks(root):
            for u, v in nx.bfs_edges(g, root):
                if u != root:
                    break
                name = g.node[v]['obj'].name
                instances = g.node[v]['obj'].instances
                if instances > 1:
                    for i in range(1, instances + 1):
                        yield _RbdBlock(name, type='Rbd block', instance=i)
                else:
                    yield _RbdBlock(name, type='Rbd block')

        def find_deepest_group(root):
            parent, node, depth = None, None, 0
            for u, v in nx.dfs_edges(g, root):
                if g.node[v]['obj'].type.lower() == 'group':
                    d = nx.shortest_path_length(g, root, v)
                    if d > depth:
                        parent, node, depth = u, v, d
            return parent, node, depth

        # Graph representing the block's internal structure
        ig = nx.DiGraph(**GRAPH_ATTRIBUTES)
        root = nx.topological_sort(g)[0]
        logic = g.node[root]['obj'].logic
        for _ in filter(lambda n: g.node[n]['obj'].type.lower() == 'group', g):
            # TODO: Handle grouped elements by using failures_graph
            _logger.debug('Block: %s, contains GROUPED components', self.name)
            while True:
                gcopy = g.copy()
                # Find the deepest Group component
                parent, node, depth = find_deepest_group(root)
                if node is None:
                    _logger.error(
                        '%s: Expected to find a GROUP component, None found',
                        self.name)
                    return  # TODO: Raise exception instead of returning
                if depth == 1:
                    break
                for u, v in nx.dfs_edges(gcopy, node):
                    g.remove_edge(u, v)
                    g.add_edge(parent, v)
                g.remove_node(node)
            # At this point, the specification graph is "normalized",
            # i.e. all Group components, apart from the root one have
            # been eliminated.
            # TODO: We can now begin building the internal graph.
            break
        else:
            if logic.name.lower() == 'and':
                for b1, b2 in window(enumerate_blocks(root)):
                    if b2 is None:
                        ig.add_node(id(b1), obj=b1)
                    else:
                        ig.add_node(id(b1), obj=b1)
                        ig.add_node(id(b2), obj=b2)
                        ig.add_edge(id(b1), id(b2))
            elif logic.name.lower() in ('or', 'active'):
                vote_val = None if logic.name.lower() == 'or' \
                    else logic.voting
                node_in = _RbdNode('{}.{}'.format(self.name, 'In'), None)
                node_out = _RbdNode('{}.{}'.format(self.name, 'Out'), vote_val)
                ig.add_node(id(node_in), obj=node_in)
                ig.add_node(id(node_out), obj=node_out)
                for b in enumerate_blocks(root):
                    ig.add_node(id(b), obj=b)
                    ig.add_edge(id(node_in), id(b))
                    ig.add_edge(id(b), id(node_out))

        self._block_graph = ig
        P = nx.drawing.nx_pydot.to_pydot(ig)
        P.write_png('/home/ergys/tmp/%s.png' % self.name)

    @property
    def name(self):
        return self._name

    @property
    def internal_graph(self):
        return self._block_graph


class _RbdBlock(object):
    """
    Class modelling an RBD block instance.
    """

    def __init__(self, name, type, instance=None):
        self._name = name
        self._type = type
        self._instance = instance

    def __str__(self):
        return '{}.{}'.format(self.name, self.instance) \
            if self._instance is not None else str(self.name)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return str(self)

    @property
    def type(self):
        return self._type

    @property
    def instance(self):
        return self._instance


class _RbdNode(object):
    """
    Class modelling an RBD node.
    """

    def __init__(self, name, vote_value=None):
        self._name = name
        self._vote_value = vote_value

    def __str__(self):
        return str(self.name)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return str(self)

    @property
    def type(self):
        return 'Rbd node'

    @property
    def vote_value(self):
        return self._vote_value

###############################################################################


class Rbd(object):
    """
    Class modelling the reliability block diagram (RBD).
    """

    def __init__(self):
        self._compound_block_index = OrderedDict()

    def from_ir_container(self, ir_container):
        """
        Constructs the RBD graph from the IR container provided.
        """
        component_graph = ir_container.component_graph
        failures_graph = ir_container.failures_graph
        self._construct_compound_blocks(component_graph, failures_graph)

    def _construct_compound_blocks(self, component_graph, failures_graph):
        g = component_graph
        f = failures_graph

        def extract_subgraph(node):
            # Given a compound node, extracts the compound component related
            # sub-graph that determines the component's internal structure.
            # Really dummy algorithm, can be improved a lot in terms of speed.
            subgraph = nx.DiGraph()
            fringe = []
            for src, dst in nx.bfs_edges(g, source=node):
                for node in fringe:
                    if nx.has_path(g, node, dst):
                        break
                else:
                    subgraph.add_edge(src, dst)
                if g.node[dst]['obj'].type.lower() == 'compound':
                    fringe.append(dst)
            for n in filter(lambda n: n in g, subgraph):
                subgraph.node[n].update(obj=g.node[n]['obj'])
            return subgraph

        def extract_failures_subgraph(node):
            for cc in nx.weakly_connected_component_subgraphs(f):
                root = nx.topological_sort(cc)[0]
                if root == node:
                    return cc

        for _, n in nx.bfs_edges(g, source=nx.topological_sort(g)[0]):
            # Traverse the components graph in BFS order.
            # For each compound element, create the internal graph.
            ndo = g.node[n]['obj']  # Associated node object
            if ndo.type.lower() == 'compound':
                _logger.debug('Constructing internal graph for: %s', ndo.name)
                block = _CompoundBlock(ndo.name)
                node_subgraph = extract_subgraph(n)
                failures_subgraph = extract_failures_subgraph(n)
                block.generate_internal_graph(node_subgraph, failures_subgraph)
                self._compound_block_index[block.name] = block

    def serialize(self, emitter):
        """Serializes the RBD by making use of the given emitter object."""
        # TODO
