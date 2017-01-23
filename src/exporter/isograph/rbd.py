"""
Module containing the classes needed to construct the reliability block diagram
for Isograph Reliability Workbench exportation.
"""

import logging
import enum
from collections import deque
from pprint import pprint

_logger = logging.getLogger('exporter.isograph.rbd')

Logic = enum.Enum('Logic', ['AND', 'OR', 'VOTE'])


class Block(object):
    """
    Class modelling an RDB block.
    """

    class _IterContents(object):
        """Iterator object to iterate through the contents of a block"""

        def __init__(self, contents):
            self._contents = contents
            self._length = len(contents)
            self._idx = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._idx == self._length:
                raise StopIteration()
            else:
                self._idx += 1
                return self._contents[self._idx - 1]

    def __init__(self, name, parent):
        self._name = name
        self._parent = parent
        self._contents_index = {}
        self._contents_list = []
        self._logic = None
        self._instance_id = None

    def __iter__(self):
        return self._IterContents(self._contents_list)

    def __repr__(self):
        return '<Block@{}#n:{}#i:{}#p:{}#l:{}'.format(
            id(self), self.name, self.instance_id, self.parent, self.logic)

    def __str__(self):
        return ('Block:\n\tName: {}\n\tInstance: {}\n\t' +
                'Parent: {} \n\tLogic: {}\n').format(
                    self.name, self.instance_id, self.parent, self.logic.logic
                    if self.logic is not None else None)

    def add_content(self, component_name, instances):
        if component_name not in self._contents_index:
            self._contents_index[component_name] = (component_name, instances)
            self._contents_list.append((component_name, instances))

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def contents(self):
        return self._contents_list

    @property
    def logic(self):
        return self._logic

    @logic.setter
    def logic(self, logic):
        self._logic = logic

    @property
    def instance_id(self):
        return self._instance_id

    @instance_id.setter
    def instance_id(self, instance_id):
        self._instance_id = instance_id


class Rbd(object):
    """
    Class modelling a RBD (Reliability Block Diagram) for Isograph.
    """

    def __init__(self, flat_container):
        self._flat_container = flat_container
        self._component_index = {}
        self._logic_index = {}
        self._block_index = {}
        self._construct()

    def _construct(self):
        self._form_basic_rdb()
        self._consider_failure_nodes()
        self._serialize_blocks()

    def _form_basic_rdb(self):
        """
        This is the first method called when constructing the RDB.
        """
        # Add logic info to the logic index
        for logic in self._flat_container.logic_list:
            self._logic_index[logic.component] = logic

        # Add system components to the component index (by name)
        for component in self._flat_container.component_list:
            self._component_index[component.name] = component
            new_block = Block(component.name, component.parent)
            # Assign logic to block
            new_block.logic = self._logic_index[component.name] \
                if component.name in self._logic_index else None
            self._block_index[component.name] = new_block

        # Create ROOT block
        self._block_index['ROOT'] = Block('ROOT', None)

        # Fill the blocks
        for name, component in self._component_index.items():
            parent = component.parent
            self._block_index[parent].add_content(name, component.quantity)

    def _consider_failure_nodes(self):
        """
        TODO
        """

    def _serialize_blocks(self):
        """
        Serializes all system RBD blocks.
        """
        # The blocks remaining to be processed. Contents shall be tuples of
        # type <Block, prefix>, where prefix is the page prefix string.
        blocks_queue = deque()
        root_block = self._block_index['ROOT']
        # Gets the system root block. Quantity shall be 1.
        name, quantity = next(iter(root_block))
        # Add the system root block to the blocks queue.
        blocks_queue.appendleft((self._block_index[name], deque(), deque()))
        while blocks_queue:
            current_block, path, old_path = blocks_queue.popleft()
            self._serialize_block(current_block, path, old_path)
            for block_name, quantity in current_block:
                block = self._block_index[block_name]
                [
                    blocks_queue.appendleft((block, path + deque([i]), path))
                    for i in range(quantity, 0, -1)
                ] if quantity > 1 else blocks_queue.appendleft(
                    (block, path, path))

    def _serialize_block(self, block, path, parent_path):
        """
        Serializes the given block to Isograph-specific tuples.
        """

        def make_path(p):
            return '.'.join([str(x) for x in p]) \
                if len(p) > 1 else str(p[0]) if len(p) == 1 else '-'

        prefix = make_path(path) if path != parent_path else ''
        parent_prefix = make_path(parent_path)
        logic = block.logic

        if logic is None:
            return

        print("{}: {}".format(block.name, logic.logic.name))

        # path_str = make_path(path)
        # old_path_str = make_path(old_path)
        # print(block)
        # print('Path: ' + path_str)
        # print('Parent path: ' + old_path_str)
        # print()
