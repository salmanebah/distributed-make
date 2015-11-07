import fileinput


class State:
    MUST_REMAKE = 0
    DONE = 1
    WAITING = 2


class ParseError(Exception):

    def __init__(self, msg):
        self.msg = msg

    
class Task:

    def __init__(self, debug_id = -1):
        self.target = None
        self.dependencies = set()
        self.command = None
        self.state = State.WAITING
        self._id = debug_id # for debugging purpose

    def __hash__(self):
        return self.target.__hash__()

    def __eq__(self, other):
        return (isinstance(other, self.__class_)) and self.target == other.target

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_debug_node(self):
        return "node" + str(self_id)

class Parser:
    _TARGET_START = '`'
    _TARGET_END = '\''
    _TARGET_START_LINE = 'Considering target file'
    _TARGET_REMAKE_LINE = 'Must remake target '
    _TARGET_PRUNE_LINE = 'Pruning file '
    _TARGET_END_LINE = 'Finished prerequisites of target file '

    def __init__(self):
        self._target_to_task = {}
        
    def _get_task_from_target(self, target):
        if target in self._target_to_task:
            return self._target_to_task[target]
        else:
            debug_id = len(self._target_to_task) + 1
            task = Task(debug_id)
            self._target_to_task[target] = task
            return task

    def _build_dependencies_tree(current_task_node):
        for line in fileinput.input():
            trimed = line.strip()
        
    def parse_makefile(self):
        pass

    def sort_tasks(self):
        pass

    def dependencies_tree_to_dot(self):
        pass
        

def _extract_target_name(line):
    start_index = line.find(_TARGET_START) + 1
    end_index = line.find(_TARGET_END)
    return line[start_index : end_index]





# class TaskCluster:
    
