"""
Isograph exporter Reliability Block Diagram (RBD) module.

Isograph system modelling is based in reliability block diagrams.
Therefore, the RBD is the core component of an Isograph model.
"""

import logging
import networkx as nx
import pydotplus

from enum import Enum
from collections import OrderedDict, deque
from itertools import groupby
from sliding_window import window
from errors import ExporterError

_logger = logging.getLogger(__name__)

# RBD elements ################################################################

GRAPH_ATTRIBUTES = dict(graph=dict(rankdir='LR'), )


def get_node_object(g, n):
    """Returns the object associated with node n from networkx graph g"""
    obj = g.node[n].get('obj')
    if obj is None:
        _logger.warning('Requested an associated object from a node, however:')
        _logger.warning('* node %s has no associated object', str(n))
    return obj


def disconnected(graph):
    return nx.number_weakly_connected_components(graph) > 1


def find_edges(graph):
    if disconnected(graph):
        return None, None
    else:
        start = next(
            filter(lambda x: graph.in_degree(x) == 0, graph.nodes_iter()))
        end = next(
            filter(lambda x: graph.out_degree(x) == 0, graph.nodes_iter()))
        return start, end


layout = Enum('layout', 'SERIES PARALLEL')


class _CompoundBlock(object):
    """
    Class modelling an RBD block.
    """

    def __init__(self, name):
        self._name = name
        self._block_graph = None
        self._dot_graph = None

    def generate_internal_graph(self, spec_graph, failures_graph):
        g = spec_graph
        f = failures_graph

        def enumerate_blocks(root):
            for u, v in nx.bfs_edges(g, root):
                if u != root:
                    break
                vo = get_node_object(g, v)
                if vo.instances > 1:
                    for i in range(1, vo.instances + 1):
                        yield _RbdBlock(vo.name, type='Rbd block', instance=i)
                else:
                    yield _RbdBlock(vo.name, type='Rbd block')

        def look_for_hint(n):
            r = next(filter(lambda x: f.in_degree(x) == 0, f.nodes_iter()))
            for u, v in nx.dfs_edges(f, r):
                if get_node_object(g, n).name == get_node_object(f, v).name:
                    logic = get_node_object(f, u).logic
                    if logic in ('or', 'active'):
                        g.node[n].update(hint=layout.PARALLEL)
                    elif logic == 'and':
                        g.node[n].update(hint=layout.SERIES)

        def create_basic_diagram(leaf):
            o = get_node_object(g, leaf)
            logic = get_node_object(g, next(nx.all_neighbors(g, leaf))).logic
            diagram = nx.DiGraph(**GRAPH_ATTRIBUTES)
            if o.instances > 1:
                if logic is None:
                    for i in range(1, o.instances + 1):
                        b = _RbdBlock(o.name, type='Rbd block', instance=i)
                        diagram.add_node(b.id, obj=b)
                    # diagram.add_nodes_from(
                    #     (_RbdBlock(o.name, type='Rbd block', instance=i)
                    #      for i in range(1, o.instances + 1)))
                elif logic == 'and':
                    for i, j in window(range(1, o.instances + 1), 2):
                        b1 = _RbdBlock(o.name, type='Rbd block', instance=i)
                        b2 = _RbdBlock(o.name, type='Rbd block', instance=j)
                        diagram.add_node(b1.id, obj=b1)
                        diagram.add_node(b2.id, obj=b2)
                        diagram.add_edge(b1.id, b2.id)
                    # diagram.add_edges_from((
                    #     (_RbdBlock(o.name, type='Rbd block', instance=i),
                    #      _RbdBlock(o.name, type='Rbd block', instance=j))
                    #     for i, j in window(range(1, o.instances + 1), 2)))
                elif logic in ('or', 'active'):
                    pass
                else:  # Invalid logic
                    _logger.error('Leaf node %s has an invalid logic', o.name)
            else:
                b = _RbdBlock(o.name, type='Rbd block')
                diagram.add_node(b.id, obj=b)
                # diagram.add_node(_RbdBlock(o.name, type='Rbd block'))
            g.node[leaf].update(diagram=diagram)

        def find_deepest_group(root):
            """
            Starting from root, finds the deepest group in spec_graph.
            Returns the deepest group itself, its depth and its parent.
            """
            node, depth, parent = None, 0, None
            for u, v in nx.dfs_edges(g, root):
                if g.node[v]['obj'].type.lower() == 'group':
                    d = nx.shortest_path_length(g, root, v)
                    if d > depth:
                        node, depth, parent = v, d, u
            return node, depth, parent

        def merge_group_diagrams(group_node):
            o = get_node_object(g, group_node)
            if o.logic is None and g.out_degree(group_node) > 1:
                _logger.error('In Group element: %s,', o.name)
                _logger.error('* element has no logic, but multiple children')
                raise ExporterError('A Group element without logic ' +
                                    'cannot have multiple children')
            o.type = 'Processed'
            if g.out_degree(group_node) == 1:
                # When the group contains only one child, avoid doing all
                # the extra work. Just take the child's diagram and remove it.
                t = next(g.neighbors_iter(group_node))
                g.node[group_node].update(
                    diagram=g.node[t].get('diagram'),
                    hint=g.node[t].get('hint'))
                g.remove_node(t)
                return
            # Group has multiple children
            nodes_to_merge = g.neighbors(group_node)
            # Find nodes with layout hint and move them to the end
            # WARNING: Due to tabular format restrictions, if the translator
            #          has gotten hints for more than one nodes, it cannot
            #          guarantee a specific output order for those nodes.
            #          The only guarantee is that they will be put at the end
            #          of the current group.
            with_hint = filter(lambda x: g.node[x].get('hint') is not None,
                               nodes_to_merge)
            with_hint = list(with_hint)
            if len(with_hint) > 1:
                _logger.warning('In Group element: %s,', o.name)
                _logger.warning(
                    '* encountered more than one children with hint')
            for x in with_hint:
                nodes_to_merge.remove(x)
                nodes_to_merge.append(x)
                g.node[group_node].update(hint=g.node[x].get('hint'))
            # Start building merged diagram
            diagram = nx.DiGraph(**GRAPH_ATTRIBUTES)
            if o.logic is None:
                _logger.error('In Group element: %s', o.name)
                _logger.error('* tried to merge the children of a Group ' +
                              'without logic')
                raise NotImplementedError(
                    'Merging Group without logic is not yet supported')
            elif o.logic == 'and':
                for n1, n2 in window(nodes_to_merge, 2):
                    if n2 is not None:
                        for i in range(o.instances):
                            n1d = g.node[n1].get('diagram')
                            n2d = g.node[n2].get('diagram')
                            d1 = get_diagram_instance(n1d, i)
                            d2 = get_diagram_instance(n2d, i)
                            diagram.add_nodes_from(d1.nodes(data=True))
                            diagram.add_nodes_from(d2.nodes(data=True))
                            diagram.add_edges_from(d1.edges())
                            diagram.add_edges_from(d2.edges())
                            s1, e1 = find_edges(d1)
                            if not disconnected(d2):
                                s2, e2 = find_edges(d2)
                                diagram.add_edge(e1, s2)
                            else:  # d2 is disconnected
                                func = nx.weakly_connected_component_subgraphs
                                for wkc in func(d2):
                                    s2, e2 = find_edges(wkc)
                                    diagram.add_edge(e1, s2)
            elif o.logic in ('or', 'active'):
                # TODO: Logic is OR or ACTIVE
                pass
            g.node[group_node].update(diagram=diagram)
            g.remove_nodes_from(nodes_to_merge)

        def get_diagram_instance(diagram, instance):
            """
            Returns an "instance" of the given diagram.
            In simple words, re-labels each node of the given diagram, so that
            they correspond to a particular instance of that diagram.
            A copy is returned, thus the given diagram remains untouched.
            """
            d = diagram.copy()  # Copy the current diagram
            for name, nodelist in groupby(
                    d.nodes_iter(), key=lambda x: get_node_object(d, x).name):
                nodelist = list(nodelist)
                length = len(nodelist)
                if length == 1:
                    o = get_node_object(d, nodelist[0])
                    old_id = o.id
                    o.instance = instance + 1
                    new_id = o.id
                    nx.relabel_nodes(d, {old_id: new_id}, copy=False)
                else:
                    for i in range(length):
                        o = get_node_object(d, nodelist[i])
                        old_id = o.id
                        current = o.instance
                        o.instance = instance * length + current
                        new_id = o.id
                        nx.relabel_nodes(d, {old_id: new_id}, copy=False)
            return d

        def apply_failure_logic(group):
            """
            Shall only be called after the grouped components have been merged.
            """
            d = g.node[group].get('diagram')

            def has_nodes(name_id):
                for n in d.nodes_iter():
                    if get_node_object(d, n).name == name_id:
                        return True
                return False

            r = next(filter(lambda x: f.in_degree(x) == 0, f.nodes_iter()))
            for u, v in nx.dfs_edges(f, r):  # Start a DFS in failures graph
                vo = get_node_object(f, v)  # Get the target object
                if vo.is_type('FailureEvent'):
                    uo = get_node_object(f, u)  # Get the source object
                    if has_nodes(vo.name):
                        # d contains nodes corresponding to the failure event
                        _logger.debug('Will apply logic: %s, to: %s.%s',
                                      uo.logic, self.name, vo.name)
                        if uo.logic in ('or', 'active'):
                            vote_val = None \
                                if uo.logic == 'or' else uo.logic.voting
                            node_out = _RbdNode('{}.Out'.format(self.name),
                                                int(vote_val))
                            d.add_node(node_out.id, obj=node_out)
                            for n in filter(
                                    lambda x: get_node_object(d, x).name == vo.name,
                                    d.nodes_iter()):
                                d.add_edge(n, node_out.id)
                        elif uo.logic == 'and':
                            for n1, n2 in window(
                                    filter(lambda x: x.name == vo.name,
                                           d.nodes_iter()), 2):
                                if n2 is not None:
                                    d.add_edge(n1, n2)

        # Graph representing the block's internal structure
        root = next(filter(lambda x: g.in_degree(x) == 0, g.nodes_iter()))
        logic = get_node_object(g, root).logic
        for _ in filter(lambda n: get_node_object(g, n).is_type('group'), g):
            # Handle grouped elements by using failures_graph
            _logger.debug('Component: %s, contains GROUPED components',
                          self.name)
            # For each leaf node, create its (temporary) diagram
            for leaf in filter(lambda x: g.out_degree(x) == 0, g.nodes_iter()):
                look_for_hint(leaf)
                create_basic_diagram(leaf)
            # Start merging and raising nodes
            while True:
                if g.number_of_nodes() == 2:
                    # Only the root node is left, we are done
                    break
                dg, dgd, dgp = find_deepest_group(root)
                merge_group_diagrams(dg)
            dg = next(g.neighbors_iter(root))
            apply_failure_logic(dg)
            ig = g.node[dg].get('diagram')
            # Needed to avoid executing the above more than once
            break  # and in order to not fall to the else clause below
        else:
            ig = nx.DiGraph(**GRAPH_ATTRIBUTES)
            if logic == 'and':
                for b1, b2 in window(enumerate_blocks(root)):
                    if b2 is None:
                        ig.add_node(b1.id, obj=b1)
                    else:
                        ig.add_node(b1.id, obj=b1)
                        ig.add_node(b2.id, obj=b2)
                        ig.add_edge(b1.id, b2.id)
            elif logic in ('or', 'active'):
                vote_val = None if logic == 'or' else logic.voting
                node_in = _RbdNode('{}.{}'.format(self.name, 'In'), None)
                node_out = _RbdNode('{}.{}'.format(self.name, 'Out'),
                                    int(vote_val))
                ig.add_node(node_in.id, obj=node_in)
                ig.add_node(node_out.id, obj=node_out)
                for b in enumerate_blocks(root):
                    ig.add_node(b.id, obj=b)
                    ig.add_edge(node_in.id, b.id)
                    ig.add_edge(b.id, node_out.id)

        self._block_graph = ig
        temp = nx.drawing.nx_pydot.to_pydot(ig)
        self._dot_graph = pydotplus.graph_from_dot_data(temp.create_dot())
        # import os
        # p = nx.drawing.nx_pydot.to_pydot(ig)
        # output_path = os.path.join(os.path.expanduser('~'), 'tmp', '{}.png')
        # p.write_png(output_path.format(self.name))

    @property
    def name(self):
        return self._name

    @property
    def internal_graph(self):
        return self._block_graph

    @property
    def internal_dot_graph(self):
        return self._dot_graph


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

    @instance.setter
    def instance(self, instance):
        self._instance = instance


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
                if get_node_object(g, dst).is_type('compound'):
                    fringe.append(dst)
            for n in filter(lambda x: x in g, subgraph):
                subgraph.node[n].update(obj=get_node_object(g, n))
            return subgraph

        def extract_failures_subgraph(node):
            for cc in nx.weakly_connected_component_subgraphs(f):
                root = nx.topological_sort(cc)[0]
                if root == node:
                    return cc

        for _, n in nx.bfs_edges(g, source=nx.topological_sort(g)[0]):
            # Traverse the components graph in BFS order.
            # For each compound element, create the internal graph.
            ndo = get_node_object(g, n)
            if ndo.is_type('compound'):
                _logger.debug('Constructing internal graph for: %s', ndo.name)
                block = _CompoundBlock(ndo.name)
                node_subgraph = extract_subgraph(n)
                failures_subgraph = extract_failures_subgraph(n)
                block.generate_internal_graph(node_subgraph, failures_subgraph)
                # export_graph_to_png(node_subgraph, ndo.name)
                self._compound_block_index[block.name] = block

    def serialize(self, emitter):
        """Serializes the RBD by making use of the given emitter object."""
        # TODO
        name, element = next(iter(self._compound_block_index.items()))
        blocks_stack = deque([(element, deque())])
        while blocks_stack:
            cblock, cpath = blocks_stack.pop()

            # import os
            # output_path = os.path.join(os.path.expanduser('~'), 'tmp', '{}.png')
            # dot_graph.write_png(output_path.format(cblock.name))

            # For each node (block) N in the current block, serialise N.
            # If it is a compound block, also add it to the stack.
            for u in nx.topological_sort(cblock.internal_graph):
                uo = cblock.internal_graph.node[u].get('obj')
                if uo.name in self._compound_block_index:
                    npath = cpath
                    if uo.instance is not None:
                        npath = npath.copy()
                        npath.append(uo.instance)
                    nblock = self._compound_block_index[uo.name]
                    blocks_stack.append((nblock, npath))
                self._serialize_element(uo, cblock, cpath,
                                        cblock.internal_dot_graph, emitter)
            # For each edge (u, v) in the current block,
            # serialise (u, v) as an RbdConnection.
            for u, v in nx.edges_iter(cblock.internal_graph):
                uo = cblock.internal_graph.node[u].get('obj')
                vo = cblock.internal_graph.node[v].get('obj')
                self._serialize_connection(cblock, cpath, uo, vo, emitter)
        emitter.commit()

    @staticmethod
    def _serialize_element(element, parent, cpath, dot_graph, emitter):
        """Serialises a single element."""

        def make_path(p):
            return '.'.join([str(t) for t in p]) + '.' \
                if len(p) > 1 else str(p[0]) + '.' if len(p) == 1 else ''

        def split_parent_path(p):
            tokens = list(p)
            if len(tokens) > 0:
                prefix = '.'.join([str(x) for x in tokens[:-1]])
                if prefix:
                    prefix = prefix + '.'
                suffix = '.'.join([str(x) for x in tokens[-1:]])
                if suffix:
                    suffix = '.' + suffix
                return prefix, suffix
            else:
                return '', ''

        s = element.id if '.' not in element.id else '"{}"'.format(element.id)
        coords = dot_graph.get_node(s)[0].get_pos().strip('"').split(',')
        xpos, ypos = [int(float(x)) for x in coords]
        prefix = Rbd._make_path(cpath)
        parent_id = Rbd._make_parent_id(parent, cpath)
        if type(element) == _RbdBlock:
            emitter.add_block(
                Id='{}{}'.format(prefix, element.id),
                Page=parent_id,
                XPosition=xpos * 1.5,
                YPosition=ypos * 1.5)
        else:
            emitter.add_node(
                Id='{}{}'.format(prefix, element.id),
                Page=parent_id,
                Vote=element.vote_value,
                XPosition=xpos * 1.5,
                YPosition=ypos * 1.5)

    @staticmethod
    def _serialize_connection(parent, cpath, src, dst, emitter):
        prefix = Rbd._make_path(cpath)
        parent_id = Rbd._make_parent_id(parent, cpath)
        src_id = '{}{}'.format(prefix, src.id)
        dst_id = '{}{}'.format(prefix, dst.id)
        identifier = '{}{}-{}'.format(prefix, src.id, dst.id)
        emitter.add_connection(identifier, parent_id, src_id, src.type, dst_id,
                               dst.type)

    @staticmethod
    def _make_path(p):
        return '.'.join([str(t) for t in p]) + '.' \
            if len(p) > 1 else str(p[0]) + '.' if len(p) == 1 else ''

    @staticmethod
    def _make_parent_id(parent, cpath):
        tokens = list(cpath)
        if len(tokens) > 0:
            prefix = '.'.join([str(x) for x in tokens[:-1]])
            if prefix:
                prefix = prefix + '.'
            suffix = '.'.join([str(x) for x in tokens[-1:]])
            if suffix:
                suffix = '.' + suffix
        else:
            prefix, suffix = '', ''
        return '{}{}{}'.format(prefix, parent.name, suffix)


# DEBUG
def export_graph_to_png(g, name):
    p = nx.drawing.nx_pydot.to_pydot(g)
    t = pydotplus.graph_from_dot_data(p.create_dot())
    t.write_png('/home/ergys/tmp/{}.png'.format(name))
