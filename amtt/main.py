"""Main entry-points.

This file contains the program's main entry points, as well as assistive
functions that perform argument parsing, PATH setup, tool initialisation, etc.
"""
import argparse
import logging
import os
import sys

from amtt.coloredtty import ColorizingStreamHandler
from amtt.loader import *

from amtt.translator import Translator


def detect_graphviz():
    """Effective for Windows systems only.

    Detects the graphviz bin directory and adds it to PATH,
    so that networkx can execute the graphviz binaries (via pydotplus).
    """
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
        choices=['isograph'],
        metavar='TARGET',
        dest='target',
        help='The target software')
    parser.add_argument(
        '-o',
        type=str,
        required=True,
        metavar='OUTPUT_BASEDIR',
        dest='output_basedir',
        help='The output base directory')
    parser.add_argument(
        '-v',
        action='count',
        dest='verbosity',
        default=0,
        help='Increase verbosity')
    parser.add_argument(
        '-x',
        '--export-graphs',
        action='count',
        default=0,
        dest='export_png',
        help='Export input model graphs as PNG images and exit')

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
    if not args.export_png and args.target is None:
        # TARGET is not required when the -x option is specified,
        # however it is required in all other cases.
        print(
            'Missing required argument: TARGET\nRe-run with -h for help.',
            file=sys.stderr)
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
        level=level,
        handlers=[ColorizingStreamHandler()])
    execute(args)
    sys.exit(0)


def execute(args):
    # call the appropriate handler for the input type
    # and get the appropriate loader
    loader = args.func(args)
    # create the Translator and start the process
    translator = Translator(loader, args.target, args.output_basedir)
    translator.parse_model()
    detect_graphviz()
    if args.export_png > 0:  # Positive value means "also export model graphs"
        translator.export_png()
    if args.export_png > 1:  # Value > 1 means "only export model graphs"
        sys.exit(0)
    translator.translate()


def ui_main():
    from amtt.ui.app import run_ui
    run_ui()
    sys.exit(0)


if __name__ == "__main__":
    if '--cli' in sys.argv:
        main()
    else:
        ui_main()

__all__ = []
