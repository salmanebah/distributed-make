"""
module to parse Makefile, build the dependencies tree
and sort the tasks of the different targets in a Makefile.
"""

import sys
import logging
import logging.config

LOGGER = logging.getLogger(__name__)

class ParseError(Exception):
    """
    Exception to signal an error during Makefiles parsing.
    """
    pass

class Task(object):
    """
    A task represent a target in the Makefile.

    Attributes:
       target (str): name of the target in the Makefile.
       dependencies(list(Task)): list of all dependencies.
       command(str): the command to execute in order to fullfill the target.
       state(State): current state of the task.
       _id(State): used only to generate the graph for dot.
    """
    def __init__(self, node_id):
        self.target = None
        self.dependencies = []
        self.command = None
        self.children = []
        self._node_id = node_id

    def __repr__(self):
        return self.target

    def __hash__(self):
        return self.target.__hash__()

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) \
               and self.target == other.target

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_file_dependency(self):
        """Returns True if this task represents a file, False otherwise."""
        return not self.dependencies and not self.command

    def get_dot_node(self):
        """Returns the node name associated with this task."""
        return "node" + str(self._node_id)

    def all_dependencies_executed(self):
        """Returns True if all dependencies have been executed,
           False otherwise."""
        return all((lambda dep: dep.executed == True)(curr_dep) \
                   for curr_dep in self.dependencies)


class Parser(object):
    """
    Parses a Makefile.

    Attributes:
      _target_to_task(dict(str, task)): dictionary to access tasks by
      target name
      _root_task(Task): default task reprensenting the root of all
      reachable the tasks
      _targets(set(str)): a set of makefile targets used to detect
      double target declarations
    """
    def __init__(self):
        LOGGER.debug('Creating Makefile parser')
        self._target_to_task = {}
        LOGGER.debug('Adding default [ROOT] target')
        self._root_task = self._get_task_from_target('[ROOT]')
        LOGGER.debug('Creating set for known makefile targets')
        self._targets = set()

    def parse_makefile(self, input_file=sys.stdin):
        """Parses the Makefile and Builds the tasks DAG.
           Raises:
             ParseError: Raised when an error is encountered
             during the parsing."""
        LOGGER.debug('Parsing Makefile from %s', input_file.name)
        LOGGER.debug('Reinitializing Parser states')
        self._root_task.dependencies = []
        self._target_to_task = {'[ROOT]' : self._root_task}
        self._targets = set()
        LOGGER.info('Reading Makefile')
        makefile_lines = input_file.readlines()
        LOGGER.info('Discarding empty lines and comment lines')
        makefile_lines = [line for line in makefile_lines
                          if not (line == '\n' or line.startswith('#'))]
        if len(makefile_lines) == 0:
            LOGGER.error('Empty Makefile')
            raise ParseError('Empty Makefile')
        index = 0
        while index < len(makefile_lines):
            current_line = makefile_lines[index]
            LOGGER.info('Analyzing %s', current_line)
            if ':' not in current_line:
                LOGGER.error('Missing : separator on line: %s', current_line)
                raise ParseError('Missing : separator on line: ' + current_line)
            if current_line.startswith('\t'):
                LOGGER.error('Expected target, found command on line: %s',
                             current_line)
                raise ParseError('Expected target, found command on line '
                                 + current_line)
            current_recipe = current_line.split(':')
            current_target = current_recipe[0].strip()
            if not current_target:
                LOGGER.error('No target found on %s', current_line)
                raise ParseError('No target specified on line ' + current_line)
            if current_target in self._targets:
                LOGGER.error('Target %s already declared', current_target)
                raise ParseError('Target ' + current_target
                                  + ' already declared')
            else:
                LOGGER.info('Adding target %s to the known targets',
                            current_target)
                self._targets.add(current_target)
            dependencies = current_recipe[1].strip()
            LOGGER.info('Creating task for target %s', current_target)
            current_task = self._get_task_from_target(current_target)
            # first target has _root_task as parent
            if index == 0:
                LOGGER.info('Adding first target %s as child of %s',
                            current_target, '[ROOT]')
                self._root_task.dependencies.append(current_task)
            for dependency in dependencies.split():
                LOGGER.info('Creating dependency task %s', dependency)
                dependency_task = self._get_task_from_target(dependency)
                LOGGER.info('Adding dependency %s for target %s',
                            dependency, current_target)
                current_task.dependencies.append(dependency_task)
            # go for the next line
            index += 1
            if index >= len(makefile_lines):
                LOGGER.info('Finishing Makefile parsing')
                break
            # get the command
            cmd = makefile_lines[index]
            if cmd.startswith('\t'):
                cmd = cmd.lstrip('\t').rstrip('\n')
                LOGGER.info('Adding command %s for target %s',
                            cmd, current_target)
                current_task.command = cmd
                index += 1
        LOGGER.info('Checking for cyclic targets')
        for task in self._target_to_task.values():
            if Parser._is_cyclically_dependent(task):
                LOGGER.error('Cyclic target %s detected', task.target)
                raise ParseError('Cyclic target ' + task.target + ' detected')

    def get_task(self, target):
        """ Returns the task associated with a target."""
        if not self._root_task.dependencies:
            LOGGER.warn('No task, empty Makefile')
        if not target:
            target_task = self._root_task.dependencies[0]
        elif target in self._target_to_task:
            target_task = self._target_to_task[target]
        else:
            LOGGER.error('No task found for target: %s', target)
            raise ParseError('No task found for target: ' + target)
        return target_task

    @staticmethod
    def _is_cyclically_dependent(task):
        """Returns True if task have dependency that depends on it,
           False otherwise. Check only for simple cyclic dependency."""
        if not task.dependencies:
            return False
        if task in task.dependencies:
            return True
        for dependency in task.dependencies:
            if task in dependency.dependencies:
                return True
        return False

    def get_dot_dependencies_tree(self):
        """Builds a digraph of the DAG for dot."""
        str_out = 'digraph G {\n'
        # build vertex
        for task in self._target_to_task.values():
            if task == self._root_task:
                continue
            str_out += task.get_dot_node()
            str_out += '[label=\"'
            str_out += task.target
            str_out += '\" color=\"'
            str_out += 'green'
            str_out += '\"];\n'
        # build edges
        for task in self._target_to_task.values():
            if task == self._root_task:
                continue
            for child_task in task.dependencies:
                str_out += child_task.get_dot_node()
                str_out += ' -> '
                str_out += task.get_dot_node()
                str_out += ';\n'
        str_out += '}'
        return str_out

    def _get_task_from_target(self, target):
        """Returns the task associated with the target name,
           Creates and Returns one if not exists.
        """
        if target in self._target_to_task:
            return self._target_to_task[target]
        else:
            node_id = len(self._target_to_task) + 1
            task = Task(node_id)
            task.target = target
            self._target_to_task[target] = task
            return task

def main():
    """Reads a makefile from stdin and prints dot commands."""
    parser = Parser()
    parser.parse_makefile()
    task = parser.get_task('')
    print '%s->' %task.target,
    for dep in task.dependencies:
        print '%s' %dep.target

if __name__ == '__main__':
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
    main()
