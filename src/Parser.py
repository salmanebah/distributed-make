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

    def __hash__(self):
        return self.target.__hash__()

    def __eq__(self, other):
        return (isinstance(other, self.__class_)) and self.target == other.target

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_debug_node(self):
        return "node" + str(self_id)

    
