"""
module to test the parsing of the Mafile in makefiles/blender_2.49
"""

import sys
import re
import unittest

sys.path.append('../src')

from Parser import Parser

class Blender249TestCase(unittest.TestCase):
    """
    Test case for Makefile in makefiles/blender_2.49.
    """
    def setUp(self):
        """Setup the test case."""
        self.makefile = open('makefiles/blender_2.49/Makefile')

    def tearDown(self):
        """ Tear down the test case."""
        self.makefile.close()

    def test_cube_is_target(self):
        """ Test that cube.mpg is valid target in the makefile
            with the expected command and dependencies."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        cube_task = parser.get_task('')
        command_parts = cube_task.command.split()
        dependency_names = [dep.target for dep in cube_task.dependencies]
        self.assertEquals(len(command_parts), 115)
        self.assertTrue(all((lambda part:
                             part == 'convert' or part == 'cube.mpg'
                             or re.match('frame_[0-9]+\.png', part)) \
                             (curr_part) for curr_part in command_parts))
        self.assertEquals(len(dependency_names), 113)
        self.assertTrue(all((lambda name: re.match('frame_[0-9]+\.png', name) \
                             (curr_name) for curr_name in dependency_names)))

    def test_cub_anim_target(self):
        """ Test that cube_anim.blend is a valid target,
             is not a file dependency and check its command."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        cube_anim_task = parser.get_task('cube_anim.blend')
        self.assertFalse(cube_anim_task.is_file_dependency())
        self.assertEquals(cube_anim_task.command,
                          'rm cube_anim.blend ; unzip cube_anim.zip')

    def test_other_target_are_frame(self):
        """ Test that all frame_[0-9]+.png are all targets, have cube_anim.blend
            as dependency and their command starts with blender."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        for i in range(1, 114):
            frame_task = parser.get_task('frame_{}.png'.format(i))
            self.assertEquals(frame_task.dependencies[0].target,
                              'cube_anim.blend')
            self.assertTrue(frame_task.command.startswith('blender'))
