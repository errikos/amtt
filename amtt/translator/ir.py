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

# IR Graph attributes
IR_GRAPH_ATTRIBUTES = {
    'node': {
        'shape': 'box',
    }
}

# Some constant declarations
RAW_INPUT_GRAPH_FILENAME = 'raw_input.png'
COMPONENT_GRAPH_FILENAME = 'components.png'
FAILURES_GRAPH_FILENAME = 'failures.png'


def is_template_def(row):
    """
    Returns whether a component row is a template definition.
    
    A component row is a template definition when his Parent is
    defined as a * (star wildcard).
    """
    return row.parent == '*'


class IRContainer(object):
    """
    Class modelling the in-memory structures container.
    """

    def __init__(self):
        self._loaded = False
        # Initialize components and failures index
        self._components_index = OrderedDict()
        self._failures_index = OrderedDict()
        # Declare graph structures
        self._raw_input_graph = None
        self._components_graph = None
        self._failures_graph = None

    def load_from_rows(self, row_container):
        """Loads the model from the provided row container."""
        _logger.info('Importing model from rows')
        self._build_graphs(row_container)
        self._loaded = True

    def _build_indexes(self, row_container):
        """
        Builds the necessary internal indexes.
        
        This method is not meant to be called from outside the class.
        """
        _logger.info('Building indexes')

    def _build_graphs(self, row_container):
        """
        Builds all necessary graphs.
        
        This method is not meant to be called from outside the class.
        """
        _logger.info('Building graphs')
        # Build raw input components graph
        self._build_raw_input_component_graph(row_container)
        # Build components graph from raw input components graph
        self._build_components_graph()

    def _build_raw_input_component_graph(self, row_container):
        """
        Builds the raw input component graph.
        
        This graph represents the relations of the components (not failures)
        as they are read by the input (i.e. further processing is required).
        
        This method is not meant to be called from outside the class.
        """

        def component(row):
            t = row.type.lower()
            return t in ('basic', 'compound',
                         'group') and not is_template_def(row)

        # Build raw input graph
        self._raw_input_graph = nx.DiGraph(
            filename=RAW_INPUT_GRAPH_FILENAME, **IR_GRAPH_ATTRIBUTES)
        rig = self._raw_input_graph
        # -- Form the graph by adding edges, nodes will be added automatically
        [
            rig.add_edge(row.parent, row.name)
            for row in row_container.component_list if component(row)
        ]
        # -- Keep name as a separate attribute because the ID will change later
        nx.set_node_attributes(rig, 'basename', {n: n for n in rig})
        # Check if raw input graph contains cycles
        if not nx.is_directed_acyclic_graph(self._raw_input_graph):
            _logger.error('Input model contains a component cycle')
            raise TranslatorError('Input model contains a component cycle')

    def _build_components_graph(self):
        """
        Given the raw input components graph (found in self),
        builds the components graph.
        
        This method has to be called after _build_raw_input_component_graph.
        This method is not meant to be called from outside the class.
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

        # -- copy the raw input graph to g
        g = self._raw_input_graph.copy()
        changed = True
        # -- Fixed-Point algorithm:
        # -- Iterate until g does not change
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
        # save g as components graph
        g.graph['filename'] = COMPONENT_GRAPH_FILENAME
        self._components_graph = g

    def export_graphs(self, output_dir):
        """
        Exports the graphs to PNG files under the <output>/graphs/ directory.
        """
        # Issue warning if method is called without loading a model
        if not self.loaded:
            _logger.warning('Exporting intermediate graphs without a model')
        # Determine and create output directory, if needed
        output_dir = os.path.join(os.path.abspath(output_dir), 'graphs')
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, mode=0o755)
        # Export graphs to image files
        glist = [
            self._raw_input_graph, self._components_graph, self._failures_graph
        ]
        for g in filter(lambda x: x is not None, glist):  # Only non-None
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
