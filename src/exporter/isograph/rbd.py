"""
Module containing the classes needed to construct the reliability block diagram
for Isograph Reliability Workbench exportation.
"""

import logging
import enum
from collections import deque
from collections import OrderedDict
from sliding_window import window
from .emitter.excel import RbdBlock, RbdNode, RbdConnection

_logger = logging.getLogger('exporter.isograph.rbd')

Logic = enum.Enum('Logic', ['AND', 'OR', 'VOTE'])


class Block(object):
    """
    Class modelling an RDB block.
    """

    def __init__(self, name, parent):
        self._name = name
        self._parent = parent
        self._contents_index = OrderedDict()
        self._logic = None
        self._instance_id = None

    def __iter__(self):
        return iter(self._contents_index.values())

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

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def contents(self):
        return self._contents_index.values()

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

    def __init__(self, flat_container, emitter):
        self._flat_container = flat_container
        self._emitter = emitter
        self._component_index = {}
        self._logic_index = {}
        self._block_index = {}
        self._construct()

    def _construct(self):
        self._form_basic_rdb()
        self._consider_failure_nodes()
        self._serialize_blocks()
        self._emitter.commit()

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
        # type <Block, prefix, parent_prefix>, where prefix is the page prefix
        # of the block and parent_prefix is the page prefix of the parent.
        blocks_stack = deque()
        root_block = self._block_index['ROOT']
        self._serialize_root(root_block)
        # Gets the system root block. Quantity shall be 1.
        name, quantity = next(iter(root_block))
        # Add the system root block to the blocks queue.
        blocks_stack.appendleft((self._block_index[name], deque(), deque()))
        while blocks_stack:
            current_block, path, parent_path = blocks_stack.popleft()
            self._serialize_block(current_block, path, parent_path)
            for block_name, quantity in current_block:
                block = self._block_index[block_name]
                [
                    blocks_stack.appendleft((block, path + deque([i]), path))
                    for i in range(quantity, 0, -1)
                ] if quantity > 1 else blocks_stack.appendleft(
                    (block, path, path))

    def _serialize_root(self, root_block):
        for block_name, _ in root_block:
            # print("{},{},{},{},{},{}".format(block_name, '', 0, 0, 0, 0))
            self._emitter.add_block(
                RbdBlock(
                    Id=block_name, Page=None, XPosition=0, YPosition=0))

    def _serialize_block(self, block, path, parent_path):
        """
        Serializes the given block to Isograph-specific tuples.
        """

        # print(block.name, path, self._block_index[block.name].parent,
        #       parent_path)

        def make_path(p):
            return '.'.join([str(t) for t in p]) \
                if len(p) > 1 else str(p[0]) if len(p) == 1 else ''

        prefix = make_path(path)

        if block.logic is None:
            return

        logic = block.logic.logic
        xs, ys = 250, 60
        dx, dy = 0, 0

        if logic is Logic.AND:
            dx, dy = 150, 0
        elif logic in (Logic.OR, Logic.VOTE):
            dx, dy = 0, 150
        if logic is Logic.VOTE:
            xs += 150

        # x, y = xs, ys

        components = []
        i = 0
        for iblock, quantity in block:
            block_obj = self._block_index[iblock]

            id_spec = '{}.{}'.format(iblock, prefix) if prefix else iblock
            if quantity > 1:  # if more than one components
                id_spec += '.{}'  # append an incremental number to the id

            for q in range(quantity):
                self._emitter.add_block(
                    RbdBlock(
                        Id=id_spec.format(q + 1),
                        Page='{}.{}'.format(block_obj.parent, prefix)
                        if prefix else block_obj.parent,
                        XPosition=xs + i * dx,
                        YPosition=ys + i * dy))
                components.append(id_spec.format(q + 1))
                i += 1

        # Create component connections
        if logic in (Logic.OR, Logic.VOTE):
            middle = len(components) / 2
            for xpos, pos in zip((xs - 150, xs + 200), ('In', 'Out')):
                self._emitter.add_node(
                    RbdNode(
                        Id='{}.{}.{}'.format(block.name, prefix, pos)
                        if prefix else '{}.{}'.format(block.name, pos),
                        Page='{}.{}'.format(block.name, prefix)
                        if prefix else block.name,
                        Vote=1,
                        XPosition=xpos,
                        YPosition=ys + middle * 150 - 50))

            input_node_index, _ = self._emitter.get_index_type_by_id(
                '{}.{}.{}'.format(block.name, prefix, 'In'))
            output_node_index, _ = self._emitter.get_index_type_by_id(
                '{}.{}.{}'.format(block.name, prefix, 'Out'))
            for i, component in enumerate(components):
                component_index, _ = self._emitter.get_index_type_by_id(
                    component)
                io_connectors = [(input_node_index, 'Rbd node',
                                  component_index, 'Rbd block'),
                                 (component_index, 'Rbd block',
                                  output_node_index, 'Rbd node')]
                for j, (input_idx, input_type, output_idx,
                        output_type) in enumerate(io_connectors):
                    self._emitter.add_connection(
                        RbdConnection(
                            Id='{}.{}.Conn.{}'.format(
                                block.name, prefix, 2 * i + (j + 1))
                            if prefix else '{}.Conn.{}'.format(
                                block.name, 2 * i + (j + 1)),
                            Page='{}.{}'.format(block.name, prefix)
                            if prefix else block.name,
                            Type='Diagonal',
                            InputObjectIndex=input_idx,
                            InputObjectType=input_type,
                            OutputObjectIndex=output_idx,
                            OutputObjectType=output_type))

        elif logic is Logic.AND:
            for i, (comp1, comp2) in enumerate(window(components, 2)):
                comp1_idx, t1 = self._emitter.get_index_type_by_id(comp1)
                comp2_idx, t2 = self._emitter.get_index_type_by_id(comp2)
                self._emitter.add_connection(
                    RbdConnection(
                        Id='{}.{}.Conn.{}'.format(
                            block.name, prefix, i + 1)
                        if prefix else '{}.Conn.{}'.format(
                            block.name, i + 1),
                        Page='{}.{}'.format(block.name, prefix)
                        if prefix else block.name,
                        Type='Diagonal',
                        InputObjectIndex=comp1_idx,
                        InputObjectType=t1,
                        OutputObjectIndex=comp2_idx,
                        OutputObjectType=t2))
