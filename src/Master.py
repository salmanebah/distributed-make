# -*- coding: utf-8 -*-
#
# this file is part of the SDCA project (team 11)
#

"""
The master's code

Divides the work into tasks and executes them with Celery
"""

from celery import group
from argparse import ArgumentParser, FileType
from Parser import Parser
from Work import run_task, RED, START_TIME, END_TIME
from time import time

class Tree(object):

    def __init__(self, task):
        stack = [task]
        self.leaves = set()
        while stack:
            node = stack.pop()
            if node.is_file_dependency():
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
    RED.flushall()
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
        if task.target == args.target and not task.is_file_dependency():
            RED.set(START_TIME, time())
            RED.set(END_TIME, time())
            res = group((run_task.s(leaf) for leaf in Tree(task).leaves))()
            res.get()
            return
    print "No rules found for target '%s'" % args.target
    

if __name__ == '__main__':
    main()
