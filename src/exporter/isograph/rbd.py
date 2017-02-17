"""
Module containing the classes needed to construct the reliability block diagram
for Isograph Reliability Workbench exportation.
"""

import logging
import re
from collections import deque
from collections import OrderedDict
from sliding_window import window
from .emitter.excel import RbdBlock, RbdNode, RbdConnection

_logger = logging.getLogger('exporter.isograph.rbd')


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
        return 'rbd.Component: t:{},n:{},c:{},i:{},p:{},L:{}'.format(
            self.type, self.name, self.code, self.instances, self.parent.name
            if self.parent is not None else None, self.logic.name
            if self.logic is not None else None)

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


class Logic(object):
    """
    Class modelling an RBD component layout:
        - ROOT: indicates the layout of the ROOT component
        - AND: connection in series
        - OR: connection in parallel
        - ACTIVE(x,y): connection in parallel with x out-of y voting
    """

    def __init__(self, raw_string):
        # Parse raw string
        tokens = re.split(r'[(,)]', raw_string)
        self._name = tokens[0]
        self._voting = tokens[1] if len(tokens) > 1 else None
        self._total = tokens[2] if len(tokens) > 2 else None

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
        self._flat_container = flat_container
        self._component_index = OrderedDict()
        self._construct()
        self._consider_failure_nodes()

    def _construct(self):
        _logger.info('Constructing in-memory RBD')
        self._form_basic_rbd()
        _logger.info('Finished constructing in-memory RBD')

    def _form_basic_rbd(self):
        # Create ROOT Component and add to index
        root = Component('COMPOUND', 'ROOT', None, 1, Logic('ROOT'))
        self._component_index[root.name] = root
        # Build component index
        for f_component in self._flat_container.component_list:
            self._component_index[f_component.name] = Component(
                f_component.element, f_component.name,
                f_component.component_code, f_component.instances)
        # Assign parents
        for f_component in self._flat_container.component_list:
            if f_component.parent not in self._component_index:
                _logger.warning('Component "{}" has an invalid parent'.format(
                    f_component.name))
            else:
                self._component_index[
                    f_component.name].parent = self._component_index[
                        f_component.parent]
        # Assign logic
        for f_logic in self._flat_container.logic_list:
            self._component_index[f_logic.gate].logic = Logic(f_logic.logic)
        # Assign children
        for name, component in self._component_index.items():
            parent = component.parent
            if parent is not None and component.type in ('compound', 'root'):
                self._component_index[parent.name].add_child(component)

    def _consider_failure_nodes(self):
        """
        TODO
        """
        for name, component in self._component_index.items():
            if component.type not in ('compound', 'root'):
                pass

    def serialize(self, emitter):
        """
        Serialize the components to the emitter.
        """
        _logger.info('Serialising RBD')
        # The components remaining to be processed. Contents shall be tuples of
        # type <Component, deque>, where deque is the page prefix of the comp.
        component_stack = deque()
        root_component = self._component_index['ROOT']
        component_stack.appendleft(
            Rbd.PreSerializedComponent(root_component, deque()))
        while component_stack:
            current = component_stack.popleft()
            self._serialize_component(current)
            for component in current.component:
                [   # If more than one instance of a component exists within
                    # another component, then append an ID to that component's
                    # path. Otherwise, just use the path of the parent.
                    component_stack.appendleft(
                        Rbd.PreSerializedComponent(component, current.path +
                                                   deque([i])))
                    for i in range(component.instances, 0, -1)
                ] if component.instances > 1 else component_stack.appendleft(
                    Rbd.PreSerializedComponent(component, current.path))

        _logger.info('Finished serialising RBD')

    def _serialize_component(self, component):
        print("Serializing: {} with path: {}".format(
            component.component, component.path))

    class PreSerializedComponent(object):
        def __init__(self, component, path):
            self.component = component
            self.path = path
