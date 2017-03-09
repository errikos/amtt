"""
Python module containing the intermediate in-memory structures of the model.
Can be considered as the Intermediate Representation (IR) of the translator.
"""

import os
import logging
import networkx as nx
from collections import OrderedDict

from .entities import SystemElement, ElementLogic

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
        self._components_graph = nx.DiGraph(
            filename='components.png', **IR_GRAPH_ATTRIBUTES)
        self._failures_graph = nx.DiGraph(
            filename='failures.png', **IR_GRAPH_ATTRIBUTES)

    def load_from_rows(self, row_container):
        """Loads the model from the provided row container"""
        _logger.info('Importing model from rows')
        self._build_lookup_indexes(row_container)
        self._build_graphs()
        self._loaded = True

    def _build_lookup_indexes(self, row_container):
        def select_index(fcomp):
            t = fcomp.type.lower()
            is_structural = t in ('basic', 'compound', 'group')
            is_failure = t in ('failurenode', 'failureevent')
            return self._components_index if is_structural \
                else self._failures_index if is_failure else None

        _logger.info('Building indexes')
        # Create a component for the Root element
        root = SystemElement('Compound', 'ROOT', 'ROOT', 1)
        root.logic = ElementLogic('ROOT')
        self._components_index[root.name] = root
        # Add the rest of the components to their respective index
        for crow in row_container.component_list:
            index = select_index(crow)
            if index is None:
                _logger.warning(
                    'Component {} has invalid Type'.format(crow.name))
            else:
                index[crow.name] = SystemElement(
                    type=crow.type,
                    name=crow.name,
                    code=crow.code,
                    instances=crow.instances)
        # Assign the element parents
        for crow in row_container.component_list:
            index = select_index(crow)
            parent_index = self._components_index \
                if crow.parent in self._components_index \
                else self._failures_index \
                if crow.parent in self._failures_index \
                else None
            if parent_index is None:
                _logger.warning(
                    'Component "{}" has an invalid parent'.format(crow.name))
            else:
                index[crow.name].parent = parent_index[crow.parent]
        # Assign logic
        for lrow in row_container.logic_list:
            index = self._components_index \
                if lrow.type.lower() == 'inherited' \
                else self._failures_index
            index[lrow.component].logic = ElementLogic(lrow.logic)

    def _build_graphs(self):
        _logger.info('Building graphs')
        # Build the components graph
        [   # Add edges
            self._components_graph.add_edge(comp.parent.id, comp.id)
            for comp in filter(lambda c: c.parent is not None,
                               self._components_index.values())
        ]
        # Associate objects
        for comp in filter(lambda c: c.name in self._components_graph,
                           self._components_index.values()):
            self._components_graph.node[comp.name].update(obj=comp)
        # Build the failures graph
        [   # Add edges
            self._failures_graph.add_edge(fail.parent.id, fail.id)
            for fail in filter(lambda f: f.parent is not None,
                               self._failures_index.values())
        ]
        # Associate objects
        for fail in filter(lambda f: f.name in self._failures_graph,
                           self._failures_index.values()):
            self._failures_graph.node[fail.name].update(obj=fail)

    def export_graphs(self, output_dir):
        """
        Exports the graphs to PNG files under the <output>/graphs/ directory.
        """
        if not self.loaded:
            _logger.warning('Exporting in-memory graphs without a model')
        output_dir = os.path.join(os.path.abspath(output_dir), 'graphs')
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, mode=0o755)
        for g in (self._components_graph, self._failures_graph):
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
