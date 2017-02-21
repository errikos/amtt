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

    @property
    def child_count(self):
        return len(self._children)


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
        self._flat_container = flat_container
        self._component_index = OrderedDict()
        self._failure_index = OrderedDict()
        self._construct()

    def _construct(self):
        _logger.info('Constructing in-memory RBD')
        # Initialise the structures from the data given
        self._initialize_structures()
        # Detect the logic of the various components,
        # for which a logic was not assigned explicitly.
        self._detect_component_logic()
        _logger.info('Finished constructing in-memory RBD')

    def _initialize_structures(self):
        # Create ROOT Component and add to index
        root = Component('Compound', 'ROOT', None, 1, Logic('ROOT'))
        self._component_index[root.name] = root
        # Build components and failures index
        for f_component in self._flat_container.component_list:
            index = self._component_index if f_component.type.lower() in (
                'compound', 'basic', 'group') else self._failure_index
            index[f_component.name] = Component(
                f_component.type, f_component.name, f_component.code,
                f_component.instances)
        # Assign parents
        for f_component in self._flat_container.component_list:
            index = self._component_index if f_component.type.lower() in (
                'compound', 'basic', 'group') else self._failure_index
            parent_index = self._component_index \
                if f_component.parent in self._component_index \
                else self._failure_index \
                if f_component.parent in self._failure_index \
                else None
            if parent_index is None:
                _logger.warning('Component "{}" has an invalid parent'.format(
                    f_component.name))
            else:
                index[f_component.name].parent = parent_index[
                    f_component.parent]
        # Assign logic
        for f_logic in self._flat_container.logic_list:
            index = self._component_index if f_logic.type.lower(
            ) == 'inherited' else self._failure_index
            index[f_logic.component].logic = Logic(f_logic.logic)
        # Assign children
        for name, component in self._component_index.items():
            parent = component.parent
            if parent is not None and component.type.lower() in (
                    'compound', 'basic', 'group'):
                self._component_index[parent.name].add_child(component)

    def _detect_component_logic(self):
        """
        For the components that have no logic assigned and no children,
        tries to figure out their logic based on the FaultNodes/FaultEvents
        in the definition.
        """
        for component in self._component_index.values():
            if component.logic is None and component.child_count > 0:
                pass

    def serialize(self, emitter):
        """
        Serialise the components to the emitter.
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
            self._serialize_component(current, emitter)
            for child in current.component:
                [   # If more than one instances of a child exist within
                    # another component, then append an ID to the child's
                    # path. Otherwise, just use the path of the parent.
                    component_stack.appendleft(
                        Rbd.PreSerializedComponent(child, current.path +
                                                   deque([i])))
                    for i in range(child.instances, 0, -1)
                ] if child.instances > 1 else component_stack.appendleft(
                    Rbd.PreSerializedComponent(child, current.path))

        _logger.info('Finished serialising RBD')

    def _serialize_component(self, packed_component, emitter):
        """
        Serialises the given PreSerializedComponent object
        to Isograph-specific tuples.
        """

        def make_path(p):
            return '.' + '.'.join([str(t) for t in p]) \
                if len(p) > 1 else '.' + str(p[0]) if len(p) == 1 else ''

        prefix = make_path(packed_component.path)
        component = packed_component.component

        # if component has no children, then nothing to do, return
        if component.child_count == 0:
            return

        if component.logic is None:
            component.logic = Logic('AND')

        # serialise the ROOT component and return
        if component.logic.name == 'ROOT':
            for child in component:
                emitter.add_block(
                    RbdBlock(
                        Id=child.name, Page=None, XPosition=0, YPosition=0))
            return

        logic = component.logic

        # set some layout specific variables
        xs, ys = 250, 60
        dx, dy = 0, 0

        if logic.name == 'AND':
            dx, dy = 150, 0
        elif logic.name in ('OR', 'ACTIVE'):
            dx, dy = 0, 150
        if logic.name == 'ACTIVE':
            xs += 150

        for block in self._layout_basic_blocks(component, prefix, xs, ys, dx,
                                               dy):
            emitter.add_block(block)

        for connection in self._layout_basic_connections():
            # emitter.add_connection(connection)
            pass

    @staticmethod
    def _layout_basic_blocks(component, prefix, xs, ys, dx, dy):
        k = 0
        for child in component:
            id_spec = '{}{}.{}' if child.instances > 1 else '{}{}'
            for i in range(child.instances):
                yield RbdBlock(
                    Id=id_spec.format(child.name, prefix, i + 1),
                    Page='{}{}'.format(child.parent.name, prefix),
                    XPosition=xs + k * dx,
                    YPosition=ys + k * dy)
                k += 1

    def _layout_basic_connections(self):
        yield

    class PreSerializedComponent(object):
        def __init__(self, component, path):
            self.component = component
            self.path = path
