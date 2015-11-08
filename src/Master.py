#! /env/bin/python
#

"""
The master's code

Divides the work into tasks and executes them with Celery
"""

from argparse import ArgumentParser, FileType

def main():
    """
    Runs a makefile on several nodes
    """
    parser = ArgumentParser(description="Distributed make")
    parser.add_argument('-f', metavar='file', dest='makefile',
                        required=True, type=FileType('r'),
                        help='the file to use')
    parser.parse_args()

if __name__ == '__main__':
    main()
