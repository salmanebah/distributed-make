# -*- coding: utf-8 -*-
#
# this file is part of the SDCA project (team 11)
#

"""
The master's code

Divides the work into tasks and executes them with Celery
"""

from celery import group, chain
from argparse import ArgumentParser, FileType
from Parser import Parser
from Work import do_task, red

def main():
    """
    Runs a makefile on several nodes
    """
    red.flushall()
    parser = ArgumentParser(description='Distributed make')
    parser.add_argument('-f', metavar='file', dest='makefile',
                        required=True, type=FileType('r'),
                        help='the file to use')
    parser.add_argument('target', nargs='?',
                        help='the makefile\'s target to create')
    args = parser.parse_args()
    makefile_parser = Parser()
    makefile_parser.parse_makefile(args.makefile)
    tasks = makefile_parser.get_sorted_tasks()

    for task in tasks:
        if task.target == args.target:
            return do_task.delay(task)
    print "No rules found for target '%s'" % args.target
    

if __name__ == '__main__':
    main()
