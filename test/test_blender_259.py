"""
module to test the parsing of the Mafile in makefiles/blender_2.59
"""

import sys
import re
import unittest

sys.path.append('../src')

from Parser import Parser

class Blender259TestCase(unittest.TestCase):
    """
    Test case for Makefile in makefiles/blender_2.59.
    """
    def setUp(self):
        """Setup the test case."""
        self.makefile = open('makefiles/blender_2.59/Makefile')

    def tearDown(self):
        """ Tear down the test case."""
        self.makefile.close()

    def test_out_is_target(self):
        """ Test that out.avi is valid target in the makefile
            with the expected command and dependencies."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        out_task = parser.get_task('out.avi')
        command = out_task.command
        dependency_names = [dep.target for dep in out_task.dependencies]
        self.assertEquals(command, 'ffmpeg -i \"f_%d.jpg\" out.avi')
        self.assertEquals(len(dependency_names), 162)
        self.assertTrue(all((lambda dep_name: re.match('f_[0-9]+\.jpg',
                                                       dep_name)) \
                             (curr_dep) for curr_dep in dependency_names))

    def test_f_are_target(self):
        """" Test that f_[0-9]+\.jpg have the expected command
             and dependencies."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        for i in range(1, 163):
            f_task = parser.get_task('f_{}.jpg'.format(i))
            self.assertTrue(f_task.command.startswith('convert')
                       or f_task.command.startswith('composite'))
            dep_name = f_task.dependencies[0].target
            self.assertTrue(dep_name.startswith('cubesphere')
                         or dep_name.startswith('dolphin')
                         or dep_name.startswith('cube_anim'))

    def test_cubesphere_are_target(self):
        """ Test that cubesphere_[0-9]+.tga are target
            with expected command and dependency."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        for i in range(1, 61):
            f_task = parser.get_task('cubesphere_{}.tga'.format(i))
            self.assertTrue(f_task.command.startswith('blender'))
            self.assertEquals(len(f_task.dependencies), 1)
            self.assertEquals(f_task.dependencies[0].target, 'cubesphere.blend')

    def test_dolphin_are_target(self):
        """ Test that dolphin_[0-9]+.tga are target
            with expected command and dependency."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        for i in range(1, 61):
            f_task = parser.get_task('dolphin_{}.tga'.format(i))
            self.assertTrue(f_task.command.startswith('blender'))
            self.assertEquals(len(f_task.dependencies), 1)
            self.assertEquals(f_task.dependencies[0].target, 'dolphin.blend')

    def test_cube_anim_are_target(self):
        """ Test that cube_anim_[0-9]+.tga are target
            with expected command and dependency."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        for i in range(1, 61):
            f_task = parser.get_task('cube_anim_{}.tga'.format(i))
            self.assertTrue(f_task.command.startswith('blender'))
            self.assertEquals(len(f_task.dependencies), 1)
            self.assertEquals(f_task.dependencies[0].target, 'cube_anim.blend')

    def test_file_dependencies(self):
        """ Test that cubesphere.blend, dolphin.blend and cube_anim.blend
            are file dependencies. """
        parser = Parser()
        parser.parse_makefile(self.makefile)
        cubesphere_task = parser.get_task('cubesphere.blend')
        dolphin_task = parser.get_task('dolphin.blend')
        cube_anim_task = parser.get_task('cube_anim.blend')
        self.assertTrue(cubesphere_task.is_file_dependency())
        self.assertTrue(dolphin_task.is_file_dependency())
        self.assertTrue(cube_anim_task.is_file_dependency())
