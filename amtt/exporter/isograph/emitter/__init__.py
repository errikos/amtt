"""Emitter module/class for Isograph."""

import os
import abc
import logging

from amtt.exporter.isograph.rows import *
from amtt.exporter import Exporter

_logger = logging.getLogger(__name__)


class IsographEmitter(object):
    """Base emitter class for Isograph."""

    def __init__(self, output_dir):
        """Initialize IsographEmitter."""
        # Setup output path
        nobasedir = output_dir is None
        basedir = output_dir if not nobasedir else ''
        output_path = 'model_{}'.format(Exporter.timestamp)
        self._output_path = os.path.join(basedir, output_path)
        _logger.info('Output path is: ' + os.path.abspath(self.output_path))
        # Initialize output row containers.
        self._blocks = []
        self._repeat_blocks = []
        self._nodes = []
        self._connections = []
        self._failure_models = []
        self._rbd_block_rule_assignments = []
        self._labors = []
        self._spares = []
        # Initialize output identifier containers.
        self._ids = {}
        # Initialize output identifier counters.
        self._next_block_id = 0
        self._next_repeat_block_id = 0
        self._next_node_id = 0

    def add_block(self, **kwargs):
        """Add an RBD block to the output."""
        self._blocks.append(RbdBlockRow(**kwargs))
        self._ids[kwargs['Id']] = self._next_block_id
        self._next_block_id += 1

    def add_repeat_block(self, **kwargs):
        """Add an RBD repeat block to the output."""
        # TODO
        pass

    def add_node(self, **kwargs):
        """Add an RBD node to the output."""
        self._nodes.append(RbdNodeRow(**kwargs))
        self._ids[kwargs['Id']] = self._next_node_id
        self._next_node_id += 1

    def add_connection(self, identifier, page, src_id, src_type, dst_id,
                       dst_type):
        """Add an RBD connection to the output."""
        src_index = self._ids[src_id]
        dst_index = self._ids[dst_id]
        connection = RbdConnectionRow(
            Id=identifier,
            Page=page,
            Type='Horizontal/vertical',
            InputObjectIndex=src_index,
            InputObjectType=src_type,
            OutputObjectIndex=dst_index,
            OutputObjectType=dst_type)
        self._connections.append(connection)

    def add_failure_model(self, name, distribution, mttf=None,
                          beta1=None, beta2=None, beta3=None,
                          eta1=None, eta2=None, eta3=None,
                          gamma1=None, gamma2=None, gamma3=None,
                          remarks=None):
        """Add a Failure Model to the output."""
        fm = FailureModelRow(
            Id=name, FmDistribution=distribution, FmMttf=mttf,
            FmBeta1=beta1, FmBeta2=beta2, FmBeta3=beta3,
            FmEta1=eta1, FmEta2=eta2, FmEta3=eta3,
            FmGamma1=gamma1, FmGamma2=gamma2, FmGamma3=gamma3,
            Remarks=remarks)
        self._failure_models.append(fm)

    def add_rbd_block_rule_assignment(self, block, dependent_block,
                                      load_factor, out_of_service, phase,
                                      type, sub_index=0):
        """Add a RbdBlockRuleAssignment to the output."""
        rule = RbdBlockRuleAssignmentRow(
            Block=block, DependentBlock=dependent_block, SubIndex=sub_index,
            LoadFactor=load_factor, OutOfService=out_of_service, Type=type)
        self._rbd_block_rule_assignments.append(rule)

    def add_labor(self, identifier, availability, cost):
        """Add a labor declaration to the output."""
        labor = LaborRow(Id=identifier,
                         NoAvailable=availability,
                         CostRate=cost)
        self._labors.append(labor)

    def add_spare(self, identifier, availability, cost):
        """Add a spare declaration to the output."""
        spare = SpareRow(Id=identifier,
                         CapacityLevel1=availability,
                         UnitCost1=cost)
        self._spares.append(spare)

    @property
    def output_path(self):
        """str: the output file path."""
        return self._output_path

    @abc.abstractmethod
    def commit(self):
        """Commit (serialize) the model to the output file."""
        raise NotImplementedError('IsographEmitter should be sub-classed')
