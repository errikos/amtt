"""
Isograph exporter Reliability Block Diagram (RBD) module.

Isograph system modelling is based in reliability block diagrams.
Therefore, the RBD is the core component of an Isograph model.

** A warning from the author **
The following is nasty code. It looks like it has been written while an
asteroid was visible from the window on its way plummeting to Earth and
finishing this module before the impact was the only hope for humanity to
survive.

I bet that this module can be re-written in a better, more organized and more
programmer (and human) friendly way. If you find yourself wasting a lot of
time trying to fix or implement something on this module, then for your own
well-being (and possibly also humanity's) please consider re-writing it.
"""

import itertools
import logging
import re
from collections import OrderedDict, deque
from enum import Enum
from itertools import groupby, chain

import networkx as nx
import pydotplus
from sliding_window import window

from amtt.errors import ExporterError

_logger = logging.getLogger(__name__)

# RBD elements ################################################################

GRAPH_ATTRIBUTES = dict(
    graph=dict(rankdir='LR'), )


def get_node_object(g, n):
    """Return the object associated with node n from networkx graph g."""
    obj = g.node[n].get('obj')
    if obj is None:
        _logger.warning('Requested an associated object from a node, however:')
        _logger.warning('-> node %s has no associated object', str(n))
    return obj


def disconnected(graph):
    """Return whether graph is a disconnected graph."""
    return nx.number_weakly_connected_components(graph) > 1


def find_edges(graph):
    """Find the first and last node of graph.

    graph shall be a directed graph (nx.DiGraph), be connected and have only
    one node with in degree = 0 and only one node with out degree = 0.

    """
    if disconnected(graph):
        return None, None
    else:
        start = next(
            filter(lambda x: graph.in_degree(x) == 0, graph.nodes_iter()))
        end = next(
            filter(lambda x: graph.out_degree(x) == 0, graph.nodes_iter()))
        return start, end


class Layout(Enum):
    """Enumeration for layout hinting."""

    series = 1
    parallel = 2


def parse_code(c):
    """Parse c as a code and format to accept instance as a format argument."""
    if re.match('^[a-zA-Z0-9\-_]*\[[Xx]\][a-zA-Z0-9\-_]*$', c):
        spec = '[X]' if '[X]' in c else '[x]'
        return c.replace(spec, '{instance}')
    else:
        return c


def logic_to_standby_mode(logic):
    """Determine standby mode for given logic."""
    if logic == 'active':
        return 'Hot'
    elif logic == 'standby':
        return 'Cold'
    else:
        return None


class _CompoundBlock(object):
    """Class modelling an RBD block."""

    def __init__(self, name, code):
        self._name = name
        self._code = parse_code(code)
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
                kwargs = dict(
                    name=vo.name,
                    code=vo.code,
                    type='Rbd block',
                    description=vo.description,
                    failure_model=vo.failure_model)
                if vo.instances > 1:
                    for i in range(1, vo.instances + 1):
                        yield _RbdBlock(**kwargs, instance=i)
                else:
                    yield _RbdBlock(**kwargs)

        def look_for_hint(n):
            r = next(filter(lambda x: f.in_degree(x) == 0, f.nodes_iter()))
            for u, v in nx.dfs_edges(f, r):
                no = get_node_object(g, n)
                to_compare = no.description if no.description else no.name
                if to_compare == get_node_object(f, v).name:
                    logic = get_node_object(f, u).logic
                    if logic in ('or', 'active', 'standby'):
                        g.node[n].update(hint=Layout.parallel)
                    elif logic == 'and':
                        g.node[n].update(hint=Layout.series)

        def create_basic_diagram(leaf):
            o = get_node_object(g, leaf)
            logic = get_node_object(g, next(nx.all_neighbors(g, leaf))).logic
            diagram = nx.DiGraph(**GRAPH_ATTRIBUTES)
            kwargs = dict(
                name=o.name,
                code=o.code,
                type='Rbd block',
                description=o.description,
                failure_model=o.failure_model)
            if o.instances > 1:
                if logic is None:
                    for i in range(1, o.instances + 1):
                        b = _RbdBlock(**kwargs, instance=i)
                        diagram.add_node(b.id, obj=b)
                elif logic == 'and':
                    for i, j in window(range(1, o.instances + 1), 2):
                        b1 = _RbdBlock(**kwargs, instance=i)
                        b2 = _RbdBlock(**kwargs, instance=j)
                        diagram.add_node(b1.id, obj=b1)
                        diagram.add_node(b2.id, obj=b2)
                        diagram.add_edge(b1.id, b2.id)
                elif logic in ('or', 'active', 'standby'):
                    pass
                else:  # Invalid logic
                    _logger.error('Leaf node %s has an invalid logic', o.name)
            else:
                b = _RbdBlock(**kwargs)
                diagram.add_node(b.id, obj=b)
            g.node[leaf].update(diagram=diagram)

        def find_deepest_group(root):
            """Find the deepest group in spec_graph, starting from root.

            Return the deepest group itself, its depth and its parent.
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
                _logger.error('-> element has no logic, but multiple children')
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
                    '-> encountered more than one children with hint')
            for x in with_hint:
                nodes_to_merge.remove(x)
                nodes_to_merge.append(x)
                g.node[group_node].update(hint=g.node[x].get('hint'))
            # Start building merged diagram
            diagram = nx.DiGraph(**GRAPH_ATTRIBUTES)
            if o.logic is None:
                _logger.error('In Group element: %s', o.name)
                _logger.error('-> tried to merge the children of a Group ' +
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
            elif o.logic in ('or', 'active', 'standby'):
                # TODO: Logic is OR or ACTIVE/STANDBY
                pass
            g.node[group_node].update(diagram=diagram)
            g.remove_nodes_from(nodes_to_merge)

        def get_diagram_instance(diagram, instance):
            """Return an "instance" of the given diagram.

            In simple words, re-label each node of the given diagram, so that
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
            """Apply the failure logic to a GROUPED component.

            Called only after the grouped components have been merged.
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
                        if uo.logic in ('or', 'active', 'standby'):
                            # Determine vote value
                            vote_val = None if uo.logic == 'or' \
                                else int(uo.logic.voting)
                            # Create output node for parallel connection
                            node_out = _RbdNode('{}.Out'.format(self.name),
                                                vote_val)
                            d.add_node(node_out.id, obj=node_out)
                            for n in filter(
                                    lambda x:
                                    get_node_object(d, x).name == vo.name,
                                    d.nodes_iter()):
                                no = get_node_object(d, n)
                                # Assign standby mode according to logic
                                no.standby_mode = logic_to_standby_mode(logic)
                                d.add_edge(n, node_out.id)
                        elif uo.logic == 'and':
                            for n1, n2 in window(
                                    filter(lambda x: x.name == vo.name,
                                           d.nodes_iter()), 2):
                                if n2 is not None:
                                    d.add_edge(n1, n2)

        def finalize_graph(graph):
            """
            Finalises the given graph.

            Sometimes, the generated internal graph may have multiple nodes
            with in_degree = 0. In those cases, we need to add a common parent
            node. Same for the output.

            Generally speaking, the internal graph must have exactly one
            entry point and exactly one exit point.
            """
            entry_points = [
                x for x in graph.nodes_iter() if graph.in_degree(x) == 0
            ]
            exit_points = [
                x for x in graph.nodes_iter() if graph.out_degree(x) == 0
            ]
            if len(entry_points) > 1:
                entry_node_id = '{}.__ENTRY_POINT'.format(self.name)
                entry_node = _RbdNode(entry_node_id, None)
                graph.add_node(entry_node.id, obj=entry_node)
                for point in entry_points:
                    graph.add_edge(entry_node.id, point)
            if len(exit_points) > 1:
                exit_node_id = '{}.__EXIT_POINT'.format(self.name)
                exit_node = _RbdNode(exit_node_id, None)
                graph.add_node(exit_node, obj=exit_node)
                for point in exit_points:
                    graph.add_edge(point, exit_node.id)

        # Graph representing the block's internal structure
        try:
            root = next(filter(lambda x: g.in_degree(x) == 0, g.nodes_iter()))
        except StopIteration:
            self._block_graph = nx.DiGraph(**GRAPH_ATTRIBUTES)
            return
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
            if logic in ('and', 'root'):
                for b1, b2 in window(enumerate_blocks(root)):
                    if b2 is None:
                        ig.add_node(b1.id, obj=b1)
                    else:
                        ig.add_node(b1.id, obj=b1)
                        ig.add_node(b2.id, obj=b2)
                        ig.add_edge(b1.id, b2.id)
            elif logic in ('or', 'active', 'standby'):
                vote_val = None if logic == 'or' else int(logic.voting)
                node_in = _RbdNode('{}.{}'.format(self.name, 'In'), None)
                node_out = _RbdNode('{}.{}'.format(self.name, 'Out'), vote_val)
                ig.add_node(node_in.id, obj=node_in)
                ig.add_node(node_out.id, obj=node_out)
                for b in enumerate_blocks(root):
                    b.standby_mode = logic_to_standby_mode(logic)
                    ig.add_node(b.id, obj=b)
                    ig.add_edge(node_in.id, b.id)
                    ig.add_edge(b.id, node_out.id)

        finalize_graph(ig)
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
    def code(self):
        return self._code

    @property
    def internal_graph(self):
        return self._block_graph

    @property
    def internal_dot_graph(self):
        return self._dot_graph


class _RbdBlock(object):
    """Class modelling an RBD block instance."""

    def __init__(self, name, code, type,
                 description=None, instance=None, standby_mode=None,
                 failure_model=None):
        self._name = name
        self._code = parse_code(code)
        self._type = type
        self._description = description
        self._instance = instance
        self._standby_mode = standby_mode
        self._failure_model = failure_model

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
    def code(self):
        return self._code

    @property
    def type(self):
        return self._type

    @property
    def description(self):
        return self._description

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, instance):
        self._instance = instance

    @property
    def standby_mode(self):
        return self._standby_mode

    @standby_mode.setter
    def standby_mode(self, standby_mode):
        self._standby_mode = standby_mode

    @property
    def failure_model(self):
        return self._failure_model


class _RbdNode(object):
    """Class modelling an RBD node.

    Only for internal use in this module.
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
    def code(self):
        return None

    @property
    def type(self):
        return 'Rbd node'

    @property
    def vote_value(self):
        return self._vote_value


###############################################################################


class Rbd(object):
    """Class modelling the reliability block diagram (RBD)."""

    def __init__(self):
        """Initialize Rbd."""
        self._compound_block_index = OrderedDict()

    def from_ir_container(self, ir_container):
        """Construct the RBD graph from the IR container provided."""
        _logger.info('Creating Isograph RBD')
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
                _, rkey = root.split('_')
                if rkey == node:
                    return cc

        root = nx.topological_sort(g)[0]
        for n in itertools.chain([root],
                                 (x for _, x in nx.bfs_edges(g, source=root))):
            # Traverse the components graph in BFS order.
            # For each compound element, create the internal graph.
            ndo = get_node_object(g, n)
            if ndo.is_type('compound'):
                _logger.debug('Constructing internal graph for: %s%s',
                              ndo.name, ' (' + ndo.description + ')'
                              if ndo.description else '')
                block = _CompoundBlock(ndo.name, ndo.code)
                node_subgraph = extract_subgraph(n)
                failures_subgraph = extract_failures_subgraph(
                    ndo.description if ndo.description else n)
                block.generate_internal_graph(node_subgraph, failures_subgraph)
                # export_graph_to_png(block.internal_graph, ndo.name)
                self._compound_block_index[block.name] = block

    def serialize(self, emitter):
        """Serialize the RBD by making use of the given emitter object."""
        _logger.info('Serializing components')
        name, element = next(iter(self._compound_block_index.items()))
        blocks_stack = deque([(element, deque(), None)])
        while blocks_stack:
            cblock, cpath, cinstance = blocks_stack.pop()
            # For each node (block) N in the current block, serialise N.
            # If it is a compound block, also add it to the stack.
            for u in nx.topological_sort(cblock.internal_graph):
                uo = cblock.internal_graph.node[u].get('obj')
                npath = cpath
                if cinstance is not None:
                    npath = npath.copy()
                    npath.append(cinstance)
                if uo.name in self._compound_block_index:
                    nblock = self._compound_block_index[uo.name]
                    blocks_stack.append((nblock, npath, uo.instance))
                self._serialize_element(uo, cblock, cpath, cinstance, emitter)
            # For each edge (u, v) in the current block,
            # serialise (u, v) as an RbdConnection.
            for u, v in nx.edges_iter(cblock.internal_graph):
                uo = cblock.internal_graph.node[u].get('obj')
                vo = cblock.internal_graph.node[v].get('obj')
                self._serialize_connection(cblock, cpath, cinstance, uo, vo,
                                           emitter)

    @staticmethod
    def _serialize_element(element, parent, ppath, pinstance, emitter):
        """Serialize a single element."""
        dot_graph = parent.internal_dot_graph

        def quote_if_necessary(element_id):
            return element_id if str.isalnum(element_id) \
                else '"{}"'.format(element.id)

        def coordinates():
            s = quote_if_necessary(element.id)
            cx, cy = dot_graph.get_node(s)[0].get_pos().strip('"').split(',')
            return int(float(cx)), int(float(cy))

        def parent_tokens():
            prefix = ppath  # The parent path, as is
            name = parent.name  # Set to parent name initially
            instance = 0 if not pinstance else pinstance
            if getattr(parent, 'code', None) and parent.code:
                name = parent.code.format(instance=instance)
                if name != parent.code:
                    instance = None
            return [x for x in chain(prefix, [name], [instance]) if x]

        def element_tokens():
            prefix = list(ppath)
            if pinstance:
                prefix.append(pinstance)
            name = element.name
            instance = 0 if not getattr(element, 'instance', None) or \
                not element.instance else element.instance
            if getattr(element, 'code', None) and element.code:
                name = element.code.format(instance=instance)
                if name != element.code:
                    instance = None
            return [x for x in chain(prefix, [name], [instance]) if x]

        # get element coordinates
        xpos, ypos = coordinates()

        # Add block/node to emitter
        kwargs = {  # Common block/node attributes
            'Id': '.'.join(str(x) for x in element_tokens()),
            'Page': '.'.join(str(x) for x in parent_tokens()),
            'XPosition': xpos * 1.75,
            'YPosition': ypos * 1.75,
        }
        if type(element) == _RbdBlock:  # Specific attributes for RBD blocks
            kwargs['Description'] = element.description
            kwargs['StandbyMode'] = element.standby_mode
            kwargs['FailureModel'] = element.failure_model
            emitter.add_block(**kwargs)
        else:  # Specific attributes for RBD nodes
            kwargs['Vote'] = element.vote_value
            emitter.add_node(**kwargs)

        return

    @staticmethod
    def _serialize_connection(parent, ppath, pinstance, src, dst, emitter):
        def make_path():
            p = ppath
            return '.'.join([str(t) for t in p]) + '.' \
                if len(p) > 1 else str(p[0]) + '.' if len(p) == 1 else ''

        def parent_tokens():
            prefix = ppath  # The parent path, as is
            name = parent.name  # Set to parent name initially
            instance = 0 if not pinstance else pinstance
            if getattr(parent, 'code', None) and parent.code:
                name = parent.code.format(instance=instance)
                if name != parent.code:
                    instance = None
            return [x for x in chain(prefix, [name], [instance]) if x]

        def element_tokens(n):
            prefix = list(ppath)
            if pinstance:
                prefix.append(pinstance)
            name = n.name
            instance = 0 if not getattr(n, 'instance', None) or \
                not n.instance else n.instance
            if getattr(n, 'code', None) and n.code:
                name = n.code.format(instance=instance)
                if name != n.code:
                    instance = None
            return [x for x in chain(prefix, [name], [instance]) if x]

        parent_id = '.'.join(str(x) for x in parent_tokens())
        src_id = '.'.join(str(x) for x in element_tokens(src))
        dst_id = '.'.join(str(x) for x in element_tokens(dst))

        prefix = make_path()
        if prefix and pinstance is not None:
            prefix = '{}{}.'.format(prefix, pinstance)
        elif pinstance is not None:
            prefix = '{}.'.format(pinstance)
        identifier = '{}{}-{}'.format(prefix, src.id, dst.id)
        emitter.add_connection(identifier, parent_id, src_id, src.type, dst_id,
                               dst.type)
