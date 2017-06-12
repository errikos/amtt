"""XML files emitter for Isograph."""
import os
import sys
import logging

from lxml import etree
from collections import OrderedDict

from amtt.exporter.isograph.rows import SCHEMA
from amtt.exporter.isograph.emitter import IsographEmitter

_logger = logging.getLogger(__name__)


def tostr(var):
    """Convert a variable to string for XML."""
    strvar = str(var)
    return strvar.lower() if type(var) == bool else strvar


class XmlEmitter(IsographEmitter):
    """XML emitter for Isograph."""

    def __init__(self, output_dir):
        """Initialize XmlEmitter."""
        # Call to super-class initializer
        super().__init__(output_dir)

    def commit(self):
        """Commit (serialize) the model to the output XML file."""
        # Determine the template XML file path
        if getattr(sys, 'frozen', False):  # Running from a bundle
            template_path = os.path.join(
                os.path.abspath(sys._MEIPASS),
                *__name__.split('.'),
                'template-2.1.xml', )
        else:  # Running from outside a bundle (e.g. pip installation)
            template_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'template-2.1.xml')
        # Open the XML file and read the XML tree into memory
        with open(template_path, 'rb') as f:
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(f, parser)
        # Fill the XML tree with the model elements
        root = tree.getroot()
        # self attributes -> SCHEMA keys mappings
        mappings = OrderedDict([
            ('_blocks', 'RbdBlocks'),
            ('_repeat_blocks', 'RbdRepeatBlocks'),
            ('_nodes', 'RbdNodes'),
            ('_connections', 'RbdConnections'),
            ('_failure_models', 'FailureModels'),
            ('_rbd_block_rule_assignments', 'RbdBlockRuleAssignments'),
            ('_labors', 'Labor'),
            ('_spares', 'Spares'),
        ])
        # Add dummy project ID (for the time being)
        xproject = etree.SubElement(root, 'Project')
        xproject_id = etree.SubElement(xproject, 'Id')
        xproject_id.text = 'AMTT_ExportedProject'
        # Iterate over mappings
        for attr, key in mappings.items():
            for row in getattr(self, attr):
                # -- create an XML sub-element for the current row
                xml_element = etree.SubElement(root, key)
                # -- add row values (columns) to XML element
                for col in SCHEMA[key]:
                    val = getattr(row, col)  # Get column from row
                    if val is None:
                        continue
                    xcol = etree.SubElement(xml_element, col)
                    xcol.text = tostr(val)
        # Write resulting XML to output path
        with open('.'.join((self.output_path, 'xml')), 'wb') as f:
            f.write(b'<?xml version="1.0" standalone="yes"?>')
            f.write(os.linesep.encode())
            et = etree.ElementTree(root)  # Convert root to ElementTree object
            et.write(f, pretty_print=True)  # Write to file
