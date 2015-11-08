"""
module to parse Makefile, build the dependencies tree
and sort the tasks of the different targets in a Makefile.
"""

import sys
# add logging

class State(object):
    """
    Different states of a task.
    """
    MUST_REMAKE = 0
    DONE = 1
    WAITING = 2


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
        self.state = State.WAITING
        self._id = debug_id # for debugging purpose

    def __hash__(self):
        return self.target.__hash__()

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) \
               and self.target == other.target

    def __ne__(self, other):
        return not self.__eq__(other)

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
    """
    _TARGET_START = '`'
    _TARGET_END = '\''
    _TARGET_START_LINE = 'Considering target file'
    _TARGET_REMAKE_LINE = 'Must remake target '
    _TARGET_PRUNE_LINE = 'Pruning file '
    _TARGET_END_LINE = 'Finished prerequisites of target file '

    def __init__(self):
        self._target_to_task = {}
        self._root_task = self._get_task_from_target('[ROOT]')


    def parse_makefile(self):
        """Parse the Makefile and Builds the tasks DAG.
        """
        while True:
            line = sys.stdin.readline()
            # EOF reached
            if not line:
                break
            line = line.strip()
            if not line.startswith(Parser._TARGET_START_LINE):
                continue
            target = Parser._extract_target_name(line)
            child_task = self._get_task_from_target(target)
            self._root_task.dependencies.append(child_task)
            self._build_dependencies_tree(child_task)

    def sort_tasks(self):
        """Sort topologically the tasks DAG.
        """
        topological_list = []
        # dependencies[0] is always Makefile so we ignore it
        first_task = self._root_task.dependencies[1]
        for dependent_task in first_task.dependencies:
            Parser._sort_tasks_aux(dependent_task, topological_list)
        topological_list.append(first_task)
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
            str_out += task.get_debug_node()
            str_out += '[label=\"'
            str_out += task.target
            str_out += '\" color=\"'
            str_out += ('red' if task.state == State.MUST_REMAKE else 'green')
            str_out += '\"];\n'
        # build edges
        for task in self._target_to_task.values():
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

    def _build_dependencies_tree(self, current_task_node):
        """Builds the DAG from the current task node.
        """
        while True:
            line = sys.stdin.readline()
            # EOF reached
            if not line:
                break
            line = line.strip()
            if line.startswith(Parser._TARGET_START_LINE):
                target = Parser._extract_target_name(line)
                child_task = self._get_task_from_target(target)
                current_task_node.dependencies.append(child_task)
                self._build_dependencies_tree(child_task)

            elif line.startswith(Parser._TARGET_REMAKE_LINE):
                target = Parser._extract_target_name(line)
                child_task = self._get_task_from_target(target)
                command = sys.stdin.readline()
                child_task.state = State.MUST_REMAKE
                child_task.command = command

            elif line.startswith(Parser._TARGET_PRUNE_LINE):
                target = Parser._extract_target_name(line)
                child_task = self._get_task_from_target(target)
                current_task_node.dependencies.append(child_task)

            elif line.startswith(Parser._TARGET_END_LINE):
                end_target = Parser._extract_target_name(line)
                if end_target != current_task_node.target:
                    raise ParseError('expected ' +
                                     current_task_node.target +
                                     ' got ' + line)
                # If the makefile is well-formed, we must finish by here
                return
        # Not well-formed Makefile
        raise ParseError(current_task_node.target)

    @staticmethod
    def _extract_target_name(line):
        """Returns the target name from the line.
        """
        start_index = line.find(Parser._TARGET_START) + 1
        end_index = line.find(Parser._TARGET_END)
        return line[start_index : end_index]


# class TaskCluster:
def main():
    """Builds a topological sort of the tasks from the Makefile in stdin."""
    parser = Parser()
    parser.parse_makefile()
    str_out = parser.dependencies_tree_to_dot()
    print str_out
    topological_list = parser.sort_tasks()
    for task in topological_list:
        print '%s->' %task.target,

if __name__ == '__main__':
    main()
