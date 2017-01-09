#!/usr/bin/env python3
"""
Main entry-point
"""
import sys
import argparse
import logging

from translator import Translator
from loader import *


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
        '-v',
        action='count',
        dest='verbosity',
        default=0,
        help='Enable verbosity')
    subparsers = parser.add_subparsers(title='Supported input types')

    # sub-parser for CSV data source
    csv_parser = subparsers.add_parser('csv', help='CSV input')
    csv_parser.add_argument(
        '-i',
        type=str,
        required=True,
        metavar='IN_DIR',
        dest='dir_in',
        help='The directory to read CSV files from')
    csv_parser.add_argument(
        '-o',
        type=str,
        default='output',
        metavar='OUT_DIR',
        dest='dir_out',
        help='The directory to write the output files to')
    # set handler function - will be called whenever the csv option is selected
    csv_parser.set_defaults(func=csv.handler)

    # sub-parser for XLS data source
    xls_parser = subparsers.add_parser('xls', help='XLS input')
    xls_parser.add_argument(
        '-i',
        type=str,
        required=True,
        metavar='IN_XLS',
        dest='xls_in',
        help='The XLS file containing the model definition')
    # set handler function - will be called whenever the xls option is selected
    xls_parser.set_defaults(func=xls.handler)

    # add subparsers for your own data sources here...

    # parse arguments and handle input type
    args = parser.parse_args()
    print(args)
    if 'func' not in args:
        parser.print_help()
        sys.exit(1)
    return args


def main():
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
    target = args.target
    # create the Translator and start the process
    translator = Translator(loader, target)
    translator.translate()


if __name__ == "__main__":
    main()
    sys.exit(0)

__all__ = []
