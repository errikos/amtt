#!/usr/bin/env python3
"""
Main entry-point
"""
import os
import sys
import argparse
import logging

from translator import Translator
from loader import *


def setup_path():
    if sys.platform != 'win32':
        return
    program_files_64 = os.path.join('C:\\', 'Program Files (x86)')
    program_files_32 = os.path.join('C:\\', 'Program Files')
    program_files_dir = program_files_64 if os.path.isdir(
        program_files_64) else program_files_32
    candidates = filter(lambda dir: dir.startswith('Graphviz'),
                        os.listdir(program_files_dir))
    graphviz_path = None
    for dir in candidates:
        graphviz_path = os.path.join(program_files_dir, dir, 'bin')
        if os.path.isdir(graphviz_path):
            break
    if not graphviz_path:
        raise OSError('Graphviz was not found. ' +
                      'Please install Graphviz and try again.')
    os.environ['PATH'] += ';' + graphviz_path


def parse_arguments():
    # parse arguments
    parser = argparse.ArgumentParser(
        description='Availability Model Translation Toolkit - AMTT')
    parser.add_argument(
        '-t',
        type=str,
        required=True,
        choices=['isograph'],
        metavar='TARGET',
        dest='target',
        help='The target software')
    parser.add_argument(
        '-o',
        type=str,
        metavar='OUTPUT_BASEDIR',
        dest='output_basedir',
        help='The output base directory')
    parser.add_argument(
        '-v',
        action='count',
        dest='verbosity',
        default=0,
        help='Increase verbosity')
    subparsers = parser.add_subparsers(title='Supported input types')

    # sub-parser for CSV data source
    csv_parser = subparsers.add_parser('csv', help='CSV input')
    csv_parser.add_argument(
        '-i',
        type=str,
        required=True,
        metavar='DIR_IN',
        dest='dir_in',
        help='The directory to read CSV files from')
    # set handler function - will be called whenever the csv option is selected
    csv_parser.set_defaults(func=csv.handler)

    # sub-parser for Excel data source
    excel_parser = subparsers.add_parser('excel', help='Microsoft Excel input')
    excel_parser.add_argument(
        '-i',
        type=str,
        required=True,
        metavar='EXCEL_IN',
        dest='excel_in',
        help='The XLS file containing the model definition')
    # set handler function - will be called whenever the xls option is selected
    excel_parser.set_defaults(func=excel.handler)

    # add subparsers for your own data sources here...

    # parse arguments and handle input type
    args = parser.parse_args()
    if 'func' not in args:
        parser.print_help()
        sys.exit(1)
    return args


def main():
    setup_path()
    args = parse_arguments()
    # configure logging
    if args.verbosity > 2:
        level = logging.DEBUG
    elif args.verbosity > 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(
        format='%(asctime)s - %(name)s:%(levelname)8s: %(message)s',
        datefmt='%H:%M:%S',
        level=level)
    # call the appropriate handler for the input type
    # and get the appropriate loader
    loader = args.func(args)
    # create the Translator and start the process
    translator = Translator(loader, args.target, args.output_basedir)
    translator.translate()


if __name__ == "__main__":
    main()
    # from ui.app import run_ui
    # run_ui()
    sys.exit(0)

__all__ = []
