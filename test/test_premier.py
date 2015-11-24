"""
module to test the parsing of the Mafile in makefiles/premier
"""

import sys
import re
import unittest

sys.path.append('../src')

from Parser import Parser

class PremierTestCase(unittest.TestCase):
    """
    Test case for Makefile in makefiles/premier.
    """
    def setUp(self):
        """Setup the test case."""
        self.makefile = open('makefiles/premier/Makefile')

    def tearDown(self):
        """ Tear down the test case."""
        self.makefile.close()

    def test_premier_is_target(self):
        """ Test that premier is a valid target in the makefile."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        target_task = [task for task in tasks if task.target == 'premier']
        self.assertIsNotNone(target_task)
        #targets = [task.target for task in tasks]
        #self.assertTrue('premier' in targets)

    def test_premier_valid_command(self):
        """ Test that the command in the premier target is valid."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        target_tasks = [task for task in tasks if task.target == 'premier']
        self.assertEquals(len(target_tasks), 1)
        self.assertEquals('gcc premier.c -o premier -lm',
                          target_tasks[0].command)

    def test_premier_dependency(self):
        """ Test that premier.c is a dependency for premier and is a file."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        premier_task = [task for task in tasks if task.target == 'premier'][0]
        self.assertEquals('premier.c', premier_task.dependencies[0].target)
        self.assertTrue(premier_task.dependencies[0].is_file_dependency())

    def test_lists_are_valid_target(self):
        """ Test that list.txt and list[1..20].txt are valid targets."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        list_tasks = [task for task in tasks if task.target.startswith('list')]
        self.assertEquals(len(list_tasks), 21)
        # check that all list[1..20].txt targets have premier as dependency
        self.assertTrue(all((lambda task:
                             task.dependencies[0].target == 'premier') \
                            (curr_task) \
                            for curr_task in list_tasks
                            if re.match('list[0-9]+\.txt', curr_task.target)))
        # check that all list[1..20]*.txt targets have command
        # starting with ./premier
        self.assertTrue(all((lambda task:
                             task.command.startswith('./premier')) \
                            (curr_task) \
                            for curr_task in list_tasks
                            if re.match('list[0-9]+\.txt', curr_task.target)))

    def test_all_targets(self):
        """ Test that all targets are either premier or
            list.txt or list[1..20].txt. """
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        target_names = [task.target for task in tasks
                        if not task.is_file_dependency()]
        self.assertEquals(len(target_names), 22)
        self.assertTrue(all((lambda name:
                             name == 'premier'
                             or re.match('list[0-9]*\.txt', name)) \
                            (curr_name) for curr_name in target_names))
