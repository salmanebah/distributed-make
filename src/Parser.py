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
        self._root_task = self._get_task_from_target('[ROOT]')


    def parse_makefile(self):
        for line in fileinput.input():
            line = line.strip()
            if not line.startswith(_TARGET_START_LINE):
                continue
            target = _extract_target_name(line)
            child_task = self._get_task_from_target(target)
            self._root_task.dependencies.add(child_task)
            _build_dependencies_tree(child_task)

    def _get_task_from_target(self, target):
        if target in self._target_to_task:
            return self._target_to_task[target]
        else:
            debug_id = len(self._target_to_task) + 1
            task = Task(debug_id)
            task.target = target
            self._target_to_task[target] = task
            return task

    def _build_dependencies_tree(current_task_node):
        for line in fileinput.input():
            line = line.strip()

            if line.startswith(_TARGET_START_LINE):
                target = _extract_target_name(line)
                child_task = self._get_task_from_target(target)
                current_task_node.dependencies.add(child_task)
                _build_dependencies_tree(child_task)

            elif line.startswith(_TARGET_REMAKE_LINE):
                target = _extract_target_name(line)
                child_task = self._get_task_from_target(target)
                command = fileinput.input().readline()
                child_task.state = State.MUST_REMAKE
                child_task.command = command

            elif line.startswith(_TARGET_PRUNE_LINE):
                target = _extract_target_name(line)
                child_task = self._get_task_from_target(target)
                current_task_node.dependencies.add(child_task)

            elif line.startswith(_TARGET_END_LINE):
                end_target = _extract_target_name(line)
                if end_target != current_task_node.target:
                    raise ParseError('expected ' +
                                     current_task_node.target +
                                     ' got ' + line)
                # If the makefile is well-formed, we must finish by here
                return
        # Not well-formed Makefile
        raise ParseError(current_task_node.target)

    def sort_tasks(self):
        pass

    def dependencies_tree_to_dot(self):
        pass
        

def _extract_target_name(line):
    start_index = line.find(_TARGET_START) + 1
    end_index = line.find(_TARGET_END)
    return line[start_index : end_index]





# class TaskCluster:
    
