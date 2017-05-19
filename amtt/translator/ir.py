"""Contains the intermediate in-memory structures of the model.

Can be considered as the Intermediate Representation (IR) of the translator.
"""

import os
import logging
import networkx as nx
from collections import OrderedDict
from copy import copy

from amtt.errors import TranslatorError
from .entities import SystemElement, ElementLogic, FailureModel

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
    """Return whether a row is a template (component) definition.

    A component row is a template definition when his Parent is
    defined as a * (star wildcard).
    """
    return row.parent == '*'


def is_component(row):
    """Return whether a row is a component definition.

    A row is a component definition if its type is Basic, Compound or Group.
    """
    t = row.type.lower()
    return t in ('basic', 'compound', 'group')


def is_failure(row):
    """Return whether a row is a failure definition.

    A row is a failure definition if its type is FailureNode or FailureEvent.
    """
    t = row.type.lower()
    return t in ('failurenode', 'failureevent')


def component_basename(node):
    """Given a component graph node, return its basename."""
    tokens = node.split('.')
    return tokens[-1]


def check_templates(row_container):
    """Check whether the model makes use of any template components."""
    clist = row_container.component_list
    if row_container.contains_templates:
        templates = set(
            c.name for c in filter(lambda x: is_template_def(x), clist))
        non_templates = set(
            c.name for c in filter(lambda x: not is_template_def(x), clist))
        return False if templates.isdisjoint(non_templates) else True
    return False


class IRContainer(object):
    """Class modelling the in-memory structures container."""

    def __init__(self):
        """Initialize IRContainer."""
        self._loaded = False
        # Initialize components and failures index
        self._components_index = OrderedDict()  # (name, parent) -> element
        self._failures_index = OrderedDict()  # name -> element
        self._failure_models_index = OrderedDict()  # name -> object
        # Declare graph structures
        self._raw_input_graph = None
        self._components_graph = None
        self._failures_graph = None
        # Whether the model uses template components
        self._uses_templates = False

    def load_from_rows(self, row_container):
        """Load the model from the provided row container."""
        _logger.info('Importing model from rows')
        self._uses_templates = check_templates(row_container)
        self._build_indexes(row_container)
        self._build_graphs(row_container)
        self._loaded = True

    def _build_indexes(self, row_container):
        """Build the necessary internal indexes.

        This method is not meant to be called from outside the class.
        """
        _logger.info('Building indexes')
        # Fill index by creating and associating the appropriate objects
        for row in row_container.component_list:
            # -- create a SystemElement object for row
            element = SystemElement(
                type=row.type,
                name=row.name,
                parent=row.parent,
                code=row.code,
                instances=row.instances)
            # -- if row represents a component, add it to components index
            if is_component(row) and not is_template_def(row):
                self._components_index[(row.name, row.parent)] = element
            # -- otherwise, add it to failures index
            # -- (completely unrelated to failure models)
            elif is_failure(row):
                self._failures_index[row.name] = element
        # Assign logic to index objects
        for row in row_container.logic_list:
            logic = ElementLogic(row.logic)  # Create a logic object
            if row.type.lower() == 'inherited':
                # -- logic entry refers to component
                for name, parent in self._components_index:
                    # -- assign logic to all objects with name == row.component
                    if name == row.component:
                        self._components_index[(name, parent)].logic = logic
            else:
                # -- logic entry refers to failure
                self._failures_index[row.component].logic = logic
        # Build failure models index
        for row in row_container.failure_models_list:
            fm = FailureModel(row.name, row.distribution, str(row.parameters),
                              row.standbystate, row.remarks)
            self._failure_models_index[fm.name] = fm
        # Process failure model -> component assignments
        for row in row_container.component_failures_list:
            fcomp = row.component
            fmodel = row.failuremodel
            if fmodel not in self._failure_models_index:
                # warn if fmodel does not name a defined model
                _logger.warning("In FailureModel to Component assignment:")
                _logger.warning("-> %s to %s", fmodel, fcomp)
                _logger.warning("-> No such failure model: %s", fmodel)
                continue
            # Assign failure model to all applicable components
            at_least_one = False
            for (comp, _), elem in self._components_index.items():
                if fcomp == comp:
                    elem.failure_model = self._failure_models_index[fmodel]
                    at_least_one = True
            if not at_least_one:  # Warn if no assignment was made
                _logger.warning("In FailureModel to Component assignment:")
                _logger.warning("-> %s to %s", fmodel, fcomp)
                _logger.warning("-> No such component: %s", fcomp)

    def _build_graphs(self, row_container):
        """Build all necessary graphs.

        This method is not meant to be called from outside the class.
        """
        _logger.info('Building graphs')
        # Build raw input components graph
        self._build_raw_input_component_graph(row_container)
        # Build components graph from raw input components graph
        self._build_components_graph()
        # Build failures graph
        self._build_failures_graph()
        # Assign objects to graph nodes
        self._assign_objects()

    def _build_raw_input_component_graph(self, row_container):
        """Build the raw input component graph.

        This graph represents the relations of the components (not failures)
        as they are read by the input (i.e. further processing is required).

        This method is not meant to be called from outside the class.
        """
        # Build raw input graph
        self._raw_input_graph = nx.DiGraph(
            filename=RAW_INPUT_GRAPH_FILENAME, **IR_GRAPH_ATTRIBUTES)
        rig = self._raw_input_graph
        # -- Form the graph by adding edges, nodes will be added automatically
        [
            rig.add_edge(row.parent, row.name)
            for row in row_container.component_list
            if is_component(row) and not is_template_def(row)
        ]
        # Check if raw input graph contains cycles
        if not nx.is_directed_acyclic_graph(self._raw_input_graph):
            _logger.error('Input model contains a component cycle')
            raise TranslatorError('Input model contains a component cycle')

    def _build_components_graph(self):
        """Build the components graph.

        Given the raw input components graph (found in self),
        build the components graph.

        This method has to be called after _build_raw_input_component_graph.
        This method is not meant to be called from outside the class.
        """
        def relabel(old_label, node):
            """Relabel old_label with respect to node.

            Relabel old_label to include the base name of node as the last
            token of its prefix.

            The label and node tokens are considered to be separated by dots.

            The node base name is its last token.

            If label contains n tokens, the prefix is considered to be the
            first n-1 tokens. Thus, s is appended to the prefix and the new
            label contains n+1 tokens.
            """
            node_tokens = node.split('.')
            tokens = old_label.split('.')
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
                    # Remove the sub-graph nodes and edges from the graph
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

    def _build_failures_graph(self):
        """Build the failure node/events graph."""
        def filter_parent(x):
            (name, parent), elem = x
            return name == element.parent

        f = nx.DiGraph(filename=FAILURES_GRAPH_FILENAME, **IR_GRAPH_ATTRIBUTES)
        # Construct the graph
        for fname, element in self._failures_index.items():
            ftype = element.type
            parent_id = element.parent
            if ftype.lower() == 'failurenode':
                # Look for parent in components index
                try:
                    _, elem = next(
                        filter(filter_parent, self._components_index.items()))
                    parent_type = elem.type
                except StopIteration:
                    # Parent not found in component index, as it should
                    _logger.error('Invalid parent name for FailureNode "%s"',
                                  fname)
                    raise TranslatorError(
                        "Error while building Failures graph. "
                        "Check log for details.")
            elif ftype.lower() == 'failureevent':
                # Look for parent in failures index
                if parent_id not in self._failures_index:
                    # Parent not found in failures index, as it should
                    _logger.error('Invalid parent name for FailureEvent "%s"',
                                  fname)
                    raise TranslatorError(
                        "Error while building Failures graph. "
                        "Check log for details.")
                parent_type = self._failures_index[parent_id].type
            parent_id = '{}_{}'.format(parent_type, parent_id)
            f.add_edge(parent_id, element.id)
        # Save g as failures graph
        self._failures_graph = f

    def _assign_objects(self):
        """Assign objects to graph nodes.

        Assign to each node of the graphs (components, failures)
        the appropriate SystemElement and ElementLogic objects.

        These objects are then used by the exporter.
        """
        # Assign objects to components graph
        g = self._components_graph
        # -- assign object for ROOT node
        ro = SystemElement('Compound', 'ROOT', None, 'ROOT', 1)
        ro.logic = ElementLogic('ROOT')
        g.node['ROOT']['obj'] = ro
        # -- assign objects for the rest of nodes
        for u, v in nx.bfs_edges(g, 'ROOT'):
            ub = component_basename(u)  # Parent base name
            vb = component_basename(v)  # Child base name
            obj = copy(self._components_index[(vb, ub)])
            obj.name = v  # Replace base name with fully qualified name
            g.node[v]['obj'] = obj
        # Assign objects to failures graph
        f = self._failures_graph
        # Failures graph is not a connected graph, but rather it has a
        # connected component for the failures of each system component.
        # -- for each root node in failures graph
        for n in filter(lambda x: f.in_degree(x) == 0, f.nodes_iter()):
            # -- root is a system component, no need to assign an object
            for u, v in nx.bfs_edges(f, n):
                _, idx_key = v.split('_')
                f.node[v]['obj'] = self._failures_index[idx_key]

    def export_graphs(self, output_dir):
        """Export the graphs to PNG files.

        Export under the <output>/graphs/ directory.
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
        """boolean: whether a model is loaded into the IRContainer."""
        return self._loaded

    @property
    def component_graph(self):
        """nx.DiGraph: the components graph."""
        return self._components_graph

    @property
    def failures_graph(self):
        """nx.DiGraph: the failures graph."""
        return self._failures_graph

    @property
    def failure_models(self):
        """list: the failure models defined in the input model."""
        return self._failure_models_index.values()

    @property
    def uses_templates(self):
        """boolean: whether the model uses template components."""
        return self._uses_templates
