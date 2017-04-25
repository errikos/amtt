"""
Python module containing the intermediate in-memory structures of the model.
Can be considered as the Intermediate Representation (IR) of the translator.
"""

import os
import logging
import networkx as nx
from collections import OrderedDict

from amtt.errors import TranslatorError

_logger = logging.getLogger(__name__)

IR_GRAPH_ATTRIBUTES = dict(
    node=dict(shape='box'), )


class IRContainer(object):
    """
    Class modelling the in-memory structures container.
    """

    def __init__(self):
        self._loaded = False
        # Initialize components and failures index
        self._components_index = OrderedDict()
        self._failures_index = OrderedDict()
        # Initialize graph structures
        self._raw_input_graph = nx.DiGraph(
            filename='raw_input.png', **IR_GRAPH_ATTRIBUTES)
        self._components_graph = nx.DiGraph(
            filename='components.png', **IR_GRAPH_ATTRIBUTES)
        self._failures_graph = nx.DiGraph(
            filename='failures.png', **IR_GRAPH_ATTRIBUTES)

    def load_from_rows(self, row_container):
        """Loads the model from the provided row container"""
        _logger.info('Importing model from rows')
        self._build_graphs(row_container)
        self._loaded = True

    def _build_graphs(self, row_container):
        _logger.info('Building graphs')
        # Build raw input graph
        [
            self._raw_input_graph.add_edge(row.parent, row.name)
            for row in row_container.component_list if row.parent != '*'
        ]
        # Check if raw input graph contains cycles
        if not nx.is_directed_acyclic_graph(self._raw_input_graph):
            _logger.error('Input model contains a component cycle')
            raise TranslatorError('Input model contains a component cycle')
        # Build components graph from raw input graph
        self._build_components_graph()

    def _build_components_graph(self):
        """
        Given the raw input graph, builds the components graph.
        """

        def relabel(label, node):
            """
            Relabels label to include the base name of node as the last token
            of its prefix.
            
            The label and node tokens are considered to be separated by dots.
            
            The node base name is its last token.
            
            If label contains n tokens, the prefix is considered to be the
            first n-1 tokens. Thus, s is appended to the prefix and the new
            label contains n+1 tokens.
            """
            node_tokens = node.split('.')
            tokens = label.split('.')
            tokens.insert(-1, str(node_tokens[-1]))
            return '.'.join(tokens)

        # -- create temporary graph, to be the components graph
        g = self._components_graph
        # -- copy the raw input graph to tmp1
        g.add_edges_from(self._raw_input_graph.edges_iter())
        changed = True
        # -- Fixed-Point algorithm:
        # -- Iterate until tmp1 and tmp2 remain identical after last iteration
        while changed:
            changed = False
            for u, v in nx.bfs_edges(g, 'ROOT'):
                if g.in_degree(v) > 1:
                    # Find the predecessors of the current node
                    predecessors = [
                        x for x in nx.all_neighbors(g, v)
                        if (x, v) in g.edges()
                    ]
                    # Disconnect predecessors from v
                    g.remove_edges_from((x, v) for x in predecessors)
                    # Clone the sub-graph which has v as its root
                    sub_graph = g.subgraph(
                        nbunch=[v] + list(nx.dfs_preorder_nodes(g, v)))
                    # Remove the sub-graph edges from the graph
                    g.remove_nodes_from(sub_graph.nodes_iter())
                    # For each predecessor, do the following:
                    for p in predecessors:
                        # -- obtain a copy of the sub-graph with renamed nodes
                        # -- by preceding the predecessor name.
                        rsub = nx.relabel_nodes(sub_graph, {
                            o: relabel(o, p)
                            for o in sub_graph.nodes_iter()
                        })
                        # -- add and connect the relabeled sub-graph (rsub)
                        # -- to the current predecessor (p)
                        g.add_edge(p, relabel(v, p))
                        g.add_edges_from(rsub.edges_iter())
                    changed = True
                    break
        # end of method

    def export_graphs(self, output_dir):
        """
        Exports the graphs to PNG files under the <output>/graphs/ directory.
        """
        if not self.loaded:
            _logger.warning('Exporting intermediate graphs without a model')
        output_dir = os.path.join(os.path.abspath(output_dir), 'graphs')
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, mode=0o755)
        for g in (self._raw_input_graph, self._components_graph,
                  self._failures_graph):
            pdg = nx.drawing.nx_pydot.to_pydot(g)
            pdg.write_png(os.path.join(output_dir, g.graph['filename']))

    @property
    def loaded(self):
        return self._loaded

    @property
    def component_graph(self):
        return self._components_graph

    @property
    def failures_graph(self):
        return self._failures_graph
