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
        tasks = parser.get_sorted_tasks()
        # raises StopIteration if not found
        out_task = next(task for task in tasks if task.target == 'out.avi')
        command = out_task.command
        dependency_names = [dep.target for dep in out_task.dependencies]
        self.assertEquals(command, 'ffmpeg -i \"f_%d.jpg\" out.avi')
        self.assertEquals(len(dependency_names), 162)
        self.assertTrue(all((lambda dep_name: re.match('f_[0-9]+\.jpg',
                                                       dep_name)) \
                             (curr_dep) for curr_dep in dependency_names))

    def test_f_are_target(self):
        """" Test that f_[0-9]+\.jpg have the expected command and dependencies."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        f_tasks = [task for task in tasks
                   if re.match('f_[0-9]+\.jpg', task.target)]
        f_cmds = [task.command for task in f_tasks]
        f_dependencies = [task.dependencies for task in f_tasks]

        self.assertTrue(all((lambda cmd: cmd.startswith('convert')
                                    or cmd.startswith('composite')) \
                             (curr_cmd) for curr_cmd in f_cmds))
        self.assertTrue(all((lambda dep: len(dep) >= 1
                             and (dep[0].target.startswith('cubesphere')
                                  or dep[0].target.startswith('dolphin')
                                  or dep[0].target.startswith('cube_anim'))) \
                            (curr_dep) for curr_dep in f_dependencies))

    def test_cubesphere_are_target(self):
        """ Test that cubesphere_[0-9]+.tga are target
            with expected command and dependency."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        cubesphere_tasks = [task for task in tasks
                           if task.target.startswith('cubesphere')
                              and task.target.endswith('tga')]
        commands = [task.command for task in cubesphere_tasks]
        dependencies = [task.dependencies for task in cubesphere_tasks]
        self.assertEquals(len(cubesphere_tasks), 60)
        self.assertTrue(all((lambda cmd: cmd.startswith('blender'))(curr_cmd) \
                             for curr_cmd in commands))
        self.assertTrue(all((lambda dep: len(dep) == 1
                             and dep[0].target == 'cubesphere.blend') \
                            (curr_dep) for curr_dep in dependencies))

    def test_dolphin_are_target(self):
        """ Test that dolphin_[0-9]+.tga are target
            with expected command and dependency."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        dolphin_tasks = [task for task in tasks
                           if task.target.startswith('dolphin')
                              and task.target.endswith('tga')]
        commands = [task.command for task in dolphin_tasks]
        dependencies = [task.dependencies for task in dolphin_tasks]
        self.assertEquals(len(dolphin_tasks), 60)
        self.assertTrue(all((lambda cmd: cmd.startswith('blender'))(curr_cmd) \
                             for curr_cmd in commands))
        self.assertTrue(all((lambda dep: len(dep) == 1
                             and dep[0].target == 'dolphin.blend') \
                            (curr_dep) for curr_dep in dependencies))

    def test_cube_anim_are_target(self):
        """ Test that cube_anim_[0-9]+.tga are target
            with expected command and dependency."""
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        cube_anim_tasks = [task for task in tasks
                           if task.target.startswith('cube_anim')
                              and task.target.endswith('tga')]
        commands = [task.command for task in cube_anim_tasks]
        dependencies = [task.dependencies for task in cube_anim_tasks]
        self.assertEquals(len(cube_anim_tasks), 60)
        self.assertTrue(all((lambda cmd: cmd.startswith('blender'))(curr_cmd) \
                             for curr_cmd in commands))
        self.assertTrue(all((lambda dep: len(dep) == 1
                             and dep[0].target == 'cube_anim.blend') \
                            (curr_dep) for curr_dep in dependencies))

    def test_file_dependencies(self):
        """ Test that cubesphere.blend, dolphin.blend and cube_anim.blend
            are file dependencies. """
        parser = Parser()
        parser.parse_makefile(self.makefile)
        tasks = parser.get_sorted_tasks()
        # raises StopIteration if not found
        cubesphere_task = next(task for task in tasks
                               if task.target == 'cubesphere.blend')
        dolphin_task = next(task for task in tasks
                               if task.target == 'dolphin.blend')
        cube_anim_task = next(task for task in tasks
                               if task.target == 'cube_anim.blend')
        self.assertTrue(cubesphere_task.is_file_dependency())
        self.assertTrue(dolphin_task.is_file_dependency())
        self.assertTrue(cube_anim_task.is_file_dependency())
