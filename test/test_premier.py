"""
module to test the parsing of the Mafile in makefiles/premier
"""

import sys
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
        task = parser.get_task('premier')
        self.assertIsNotNone(task)

    def test_premier_valid_command(self):
        """ Test that the command in the premier target is valid."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        task = parser.get_task('premier')
        self.assertEquals('gcc premier.c -o premier -lm',
                          task.command)

    def test_premier_dependency(self):
        """ Test that premier.c is a dependency for premier and is a file."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        task = parser.get_task('premier')
        self.assertEquals('premier.c', task.dependencies[0].target)
        self.assertTrue(task.dependencies[0].is_file_dependency())

    def test_lists_are_valid_target(self):
        """ Test that list[1..20].txt are valid targets."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        for i in range(1, 21):
            task = parser.get_task('list{}.txt'.format(i))
            self.assertTrue(task.dependencies[0].target == 'premier')
            self.assertTrue(task.command.startswith('./premier'))

    def test_all_targets(self):
        """ Test that list.txt is the default target. """
        parser = Parser()
        parser.parse_makefile(self.makefile)
        task = parser.get_task('')
        self.assertTrue(task.target == 'list.txt')
        self.assertEquals(len(task.dependencies), 20)
