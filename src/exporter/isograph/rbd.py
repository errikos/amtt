"""
Module containing the classes needed to construct the reliability block diagram
for Isograph Reliability Workbench exportation.
"""

import os
import logging
import re
import networkx as nx
from collections import OrderedDict
from copy import copy

_logger = logging.getLogger(__name__)


class Component(object):
    """
    Class modelling an RBD component.
    """

    def __init__(self, type, name, code, instances, logic=None):
        self._type = type
        self._name = name
        self._code = code
        self._instances = instances
        self._logic = logic
        self._parent = None
        self._children = []

    def __str__(self):
        # return 'rbd.Component: c:{},i:{},p:{},L:{}'.format(
        #     self.name, self.instances,
        #     self.parent.name if self.parent is not None else None,
        #     self.logic.name if self.logic is not None else None)
        return '{}: {}'.format(self.type, self.name)

    def __iter__(self):
        return iter(self._children)

    def add_child(self, component):
        self._children.append(component)

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code

    @property
    def instances(self):
        return self._instances

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def logic(self):
        return self._logic

    @logic.setter
    def logic(self, logic):
        self._logic = logic

    @property
    def child_count(self):
        return len(self._children)


class ComponentInstance(object):
    def __init__(self, component, instance):
        self._component = component
        self._instance = instance

    @property
    def component(self):
        """Returns the component object (metaclass) of the instance"""
        return self._component

    @property
    def instance(self):
        """Returns the instance number of the instance"""
        return self._instance

    @property
    def full_name(self):
        """Returns the fully qualified name of the instance"""
        return '.'.join((self.component.name, str(self.instance)))


class Logic(object):
    """
    Class modelling an RBD component layout:
        - ROOT: indicates the layout of the ROOT component,
                should only be used for the ROOT component
        - AND: connection in series
        - OR: connection in parallel
        - ACTIVE(x,y): connection in parallel with x out-of y voting
        - SERIES: layout in series
        - PARALLEL: layout in parallel
    """

    def __init__(self, raw_string):
        # Parse raw string
        tokens = re.split(r'[(,)]', raw_string)
        self._name = tokens[0]
        self._voting = tokens[1] if len(tokens) > 1 else None
        self._total = tokens[2] if len(tokens) > 2 else None

    def __eq__(self, other):
        return self.name == other.name \
               and self.voting == other.voting \
               and self.total == other.total

    def __str__(self):
        s = 'Logic: ' + self._name
        if self._name == 'ACTIVE':
            s += ', {} out of {}'.format(self._voting, self._total)
        return s

    @property
    def name(self):
        return self._name

    @property
    def voting(self):
        return self._voting

    @property
    def total(self):
        return self._total


class Rbd(object):
    """
    Class modelling a RBD (Reliability Block Diagram) for Isograph.
    """

    def __init__(self, flat_container):
        # Initialize components and failures index
        self._components_index = OrderedDict()
        self._failures_index = OrderedDict()
        # Initialize graph structures
        self._input_graph = nx.DiGraph()
        self._components_graph = nx.DiGraph()
        self._failures_graph = nx.DiGraph()
        self._output_graph = nx.DiGraph()
        # Construct the RBD
        self._import(flat_container)
        # DEBUG
        # self.print_indexes()

    def _import(self, flat_container):
        _logger.info("Importing model definition in memory")
        self._build_lookup_indexes(flat_container)
        self._build_graphs()

    def _build_lookup_indexes(self, flat_container):
        def select_index(fcomp):
            t = fcomp.type.lower()
            is_structural = t in ('basic', 'compound', 'group')
            is_failure = t in ('failurenode', 'failureevent')
            return self._components_index if is_structural \
                else self._failures_index if is_failure else None

        _logger.info("Building indexes")
        # Create a component for the Root node
        root = Component('Compound', 'ROOT', None, 1, Logic('ROOT'))
        self._components_index[root.name] = root
        # Add the rest of the components to its respective index
        for fcomp in flat_container.component_list:
            index = select_index(fcomp)
            if index is None:
                _logger.warning(
                    "Component {} has invalid Type".format(fcomp.name))
            else:
                index[fcomp.name] = Component(
                    type=fcomp.type,
                    name=fcomp.name,
                    code=fcomp.code,
                    instances=fcomp.instances)
        # Assign the component parents
        for fcomp in flat_container.component_list:
            index = select_index(fcomp)
            parent_index = self._components_index \
                if fcomp.parent in self._components_index \
                else self._failures_index \
                if fcomp.parent in self._failures_index \
                else None
            if parent_index is None:
                _logger.warning(
                    'Component "{}" has an invalid parent'.format(fcomp.name))
            else:
                # if parent_index != index:
                #     p = copy(parent_index[fcomp.parent])
                #     p.parent = None
                #     index[p.name] = p
                index[fcomp.name].parent = parent_index[fcomp.parent]
        # Assign logic
        for f_logic in flat_container.logic_list:
            index = self._components_index if f_logic.type.lower(
            ) == 'inherited' else self._failures_index
            index[f_logic.component].logic = Logic(f_logic.logic)

    def _build_graphs(self):
        _logger.info("Building graphs")
        # Build the components graph
        [   # Add edges
            self._components_graph.add_edge(comp.parent, comp)
            for comp in filter(lambda c: c.parent is not None,
                               self._components_index.values())
        ]
        # Build the failures graph
        [   # Add edges
            self._failures_graph.add_edge(fail.parent, fail)
            for fail in filter(lambda f: f.parent is not None,
                               self._failures_index.values())
        ]
        self.export_graphs()

    def export_graphs(self):
        """Exports the graphs to PNG files under the ./graphs/ directory"""
        output_dir = os.path.join(os.path.abspath(os.path.curdir), 'graphs')
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir, mode=0o755)
        p = nx.drawing.nx_pydot.to_pydot(self._components_graph)
        p.write_png(os.path.join(output_dir, 'components.png'))
        p = nx.drawing.nx_pydot.to_pydot(self._failures_graph)
        p.write_png(os.path.join(output_dir, 'failures.png'))

    @staticmethod
    def _layout_graph(graph):
        ts_list = nx.topological_sort(graph)
        L = nx.bfs_successors(graph, ts_list[0])
        pos = {ts_list[0]: (0, 0)}
        dx, dy = 5, 3
        x, y = dx, 0
        for node in ts_list:
            if node in L:
                for v in L[node]:
                    pos[v] = (x, y)
                    y += dy
                x += dx
                y = 0
        return pos

    def print_indexes(self):
        """DEBUG"""
        print("=== Components")
        for comp in self._components_index.values():
            print(comp)
        print("===")

        print("=== Failures")
        for comp in self._failures_index.values():
            print(comp)
        print("===")
