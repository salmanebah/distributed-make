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
        self.executed = False
        self._node_id = node_id

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
      _root_task(Task): default task reprensenting the root of all the tasks
    """
    def __init__(self):
        LOGGER.debug('Creating Makefile parser')
        self._target_to_task = {}
        LOGGER.debug('Adding default [ROOT] target')
        self._root_task = self._get_task_from_target('[ROOT]')

    def parse_makefile(self, input_file=sys.stdin):
        """Parses the Makefile and Builds the tasks DAG."""
        LOGGER.debug('Parsing Makefile from %s', input_file.name)
        LOGGER.debug('Reinitializing Parser states')
        self._root_task.dependencies = []
        self._target_to_task = {'[ROOT]' : self._root_task}
        LOGGER.info('Reading Makefile')
        makefile_lines = input_file.readlines()
        LOGGER.info('Discarding empty lines and comment lines')
        makefile_lines = [line for line in makefile_lines
                          if not (line == '\n' or line.startswith('#'))]
        index = 0
        while index < len(makefile_lines):
            current_line = makefile_lines[index]
            LOGGER.info('Analyzing %s', current_line)
            current_recipe = current_line.split(':')
            current_target = current_recipe[0].strip()
            if not current_target:
                LOGGER.error('No target found on %s', current_line)
                raise ParseError('No target specified on line ' + current_line)
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

    def get_sorted_tasks(self):
        """Returns the tasks sorted topologically."""
        LOGGER.info('Sorting tasks topologically')
        topological_list = []
        # if _root_task has no dependency, the parsed Makefile was empty
        if not self._root_task.dependencies:
            LOGGER.info('Finishing the sorting, empty Makefile')
            return topological_list
        # Only one task as dependency for root
        LOGGER.info('Getting the first task')
        first_task = self._root_task.dependencies[0]
        LOGGER.info('Start sorting dependencies for the first task: %s',
                    first_task.target)
        for dependent_task in first_task.dependencies:
            LOGGER.info('Sorting dependencies for %s', dependent_task.target)
            Parser._sort_tasks_aux(dependent_task, topological_list)
        LOGGER.info('End sorting dependencies for the first task')
        LOGGER.info('Adding the first task %s in the sorted list',
                    first_task.target)
        topological_list.append(first_task)
        # add all tasks which no other task depends on
        LOGGER.info('Adding file dependencies (if any)')
        for independant_task in self._target_to_task.values():
            if independant_task not in topological_list and \
               independant_task != self._root_task:
                topological_list.insert(0, independant_task)
        return topological_list

    @staticmethod
    def _sort_tasks_aux(current_task_node, topological_list):
        """Sorts recursively the DAG with a postfix traversal."""
        # a task without dependency
        if not current_task_node.dependencies:
            # the first time we visit the leaf
            if not current_task_node in topological_list:
                topological_list.append(current_task_node)
        else:
            for dependent_task in current_task_node.dependencies:
                Parser._sort_tasks_aux(dependent_task, topological_list)
            # the first time we visit the node
            if not current_task_node in topological_list:
                topological_list.append(current_task_node)

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
    sorted_tasks = parser.get_sorted_tasks()
    for task in sorted_tasks:
        print '%s->' %task.target,

if __name__ == '__main__':
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
    main()
