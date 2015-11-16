"""
module to parse Makefile, build the dependencies tree
and sort the tasks of the different targets in a Makefile.
"""

import sys
# add logging

class ParseError(Exception):
    """
    Exception to signal an error during Makefiles parsing.
    """
    def __init__(self, msg):
        super(ParseError, self).__init__()
        self.msg = msg

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
    def __init__(self, debug_id=-1):
        self.target = None
        self.dependencies = []
        self.command = None
        self.executed = False
        self._id = debug_id # for debugging purpose

    def __hash__(self):
        return self.target.__hash__()

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) \
               and self.target == other.target

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '<' + self.target + ',' + self.command + ', ' \
               + str(self.dependencies) + '>'

    def is_file_dependency(self):
        """Returns True if this task represents a file, False otherwise."""
        return not self.dependencies and not self.command

    def get_debug_node(self):
        """Returns the node associated with the task."""
        return "node" + str(self._id)

class Parser(object):
    """
    Parses a Makefile.

    Attributes:
      _target_to_task(dict(str, task)): dictionary to access tasks by
      target name
      _root_task(Task): default task reprensenting the root of all the tasks
      _input_file(file): the input file to read from
    """
    def __init__(self, input_file=sys.stdin):
        self._target_to_task = {}
        self._root_task = self._get_task_from_target('[ROOT]')
        self._input_file = input_file


    def parse_makefile(self):
        """Parse the Makefile and Builds the tasks DAG."""
        makefile_lines = self._input_file.readlines()
        makefile_lines = [line for line in makefile_lines if line != '\n']
        for index in range(0, len(makefile_lines), 2):
            current_line = makefile_lines[index]
            current_recipe = current_line.split(':')
            current_target = current_recipe[0].strip()
            if not current_target:
                raise ParseError('No target specified on line ' + current_line)
            dependencies = current_recipe[1].strip()
            current_task = self._get_task_from_target(current_target)
            # first target has _root_task as parent
            if index == 0:
                self._root_task.dependencies.append(current_task)
            for dependency in dependencies.split():
                dependency_task = self._get_task_from_target(dependency)
                current_task.dependencies.append(dependency_task)
            # get the command
            cmd = makefile_lines[index + 1]
            if not cmd.startswith('\t'):
                raise ParseError('No command specified for target '
                                 + current_target)
            current_task.command = cmd.strip('\t')

    def sort_tasks(self):
        """Sort topologically the tasks DAG."""
        topological_list = []
        # Only one task as dependency for root
        first_task = self._root_task.dependencies[0]
        for dependent_task in first_task.dependencies:
            Parser._sort_tasks_aux(dependent_task, topological_list)
        topological_list.append(first_task)
        # add all tasks which no other task depends on
        for independant_task in self._target_to_task.values():
            if independant_task not in topological_list and \
               independant_task != self._root_task:
                topological_list.insert(0, independant_task)
        return topological_list

    @staticmethod
    def _sort_tasks_aux(current_task_node, topological_list):
        """Sorts recursively the DAG with a postfix traversal.
        """
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

    def dependencies_tree_to_dot(self):
        """Builds a digraph of the DAG for dot.
        """
        str_out = 'digraph G {\n'
        # build vertex
        for task in self._target_to_task.values():
            if task == self._root_task:
                continue
            str_out += task.get_debug_node()
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
                str_out += child_task.get_debug_node()
                str_out += ' -> '
                str_out += task.get_debug_node()
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
            debug_id = len(self._target_to_task) + 1
            task = Task(debug_id)
            task.target = target
            self._target_to_task[target] = task
            return task


def main():
    """Builds a topological sort of the tasks from the Makefile in stdin."""
    parser = Parser()
    parser.parse_makefile()
    str_out = parser.dependencies_tree_to_dot()
    print str_out
    topological_list = parser.sort_tasks()
    # for task in topological_list:
    #     print '%s->' %task.target,
    #     print '%s->' %task.command,

if __name__ == '__main__':
    main()
