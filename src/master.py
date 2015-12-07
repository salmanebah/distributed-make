# -*- coding: utf-8 -*-
#
# this file is part of the SDCA project (team 11)
#

"""
The master's code

Divides the work into tasks and executes them with Celery
"""

from argparse import ArgumentParser, FileType
from celery import group
from os.path import exists
from makeparse import Parser
from work import run_task, RED, START_TIME, END_TIME
from time import time

class DepTree(object):
    """
    A dependency tree
    """

    def __init__(self, task):
        """
        Creates a DepTree from a task

        The idea is to iterate through the task's dependencies
        and add every task to the tree. The tasks without any
        dependencies are stored in the ``leaves`` attr of the tree.
        The attr ``children`` of the tasks we iterate on is set
        so that we can easily iterate on the tree nodes from the
        leaves to the root.
        """

        # Classical algorithm to iterate on a tree's nodes using
        # a stack
        stack = [task]
        self.leaves = set()
        while stack:
            node = stack.pop()
            if node.is_file_dependency():
                # A task can be just a file that is required before
                # executing the makefile, we do not care about those
                continue
            node.dependencies = [dep for dep in node.dependencies
                                 if not dep.is_file_dependency()]
            if not node.dependencies:
                self.leaves.add(node)
                continue
            for dep in node.dependencies:
                dep.children.append(node)
                stack.append(dep)

def main():
    """
    Runs a makefile on several nodes
    """
    # Flush the database, from one execution to another
    RED.flushdb()

    # The makefile to use in case none is provided
    default_makefile = None
    for makefile in ('GNU-makefile', 'makefile', 'Makefile'):
        if exists(makefile):
            default_makefile = makefile

    # Parse the args from the command line
    parser = ArgumentParser(description='Distributed make')
    parser.add_argument('-f', metavar='file', nargs='?', dest='makefile',
                        type=FileType('r'), default=default_makefile,
                        help='the file to use')
    parser.add_argument('target', nargs='?', default="",
                        help='the makefile\'s target to create')
    args = parser.parse_args()

    if args.makefile is None:
        print "No makefile was found. Stopping."
        return

    # Initialize the start_time and the end_time (for the measures)
    RED.set(START_TIME, time())
    RED.set(END_TIME, time())

    # Parse the makefile
    makefile_parser = Parser()
    makefile_parser.parse_makefile(args.makefile)

    # Fetch the target
    task = makefile_parser.get_task(args.target)

    if not task.is_file_dependency():
        # Create a dependency tree and launch all the leaves
        # in parrallel
        group((run_task.s(leaf) for leaf in DepTree(task).leaves))()

if __name__ == '__main__':
    main()
