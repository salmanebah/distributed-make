# -*- coding: utf-8 -*-
#
# this file is part of the SDCA Project (team 11)
#

"""
This module contains the code used by the slave nodes
"""

from celery import Celery, group
from celeryconfig import MASTER_NODE
from celery.signals import task_postrun
# Import the Task so that it can be deserialized by celery
from makeparse import Task
from os import system
from redis import Redis
from time import time

APP = Celery()
# Configure Celery
APP.config_from_object('celeryconfig')

START_TIME = "start_time"
END_TIME = "end_time"

TASK_NUM = "task_num"
END_LIST = "endlist"
SLAVE_LOCK = "slavelock"

RED = Redis(host=MASTER_NODE)

@APP.task
def run_task(task):
    """
    Runs a task
    """
    # We create two names that are specific to a given task
    lock_name = task.target + "_lock"
    # This is more of a counter than a semaphore, but I like it
    sem_name = task.target + "_sem"

    # Acquire the lock specific to this task
    # Mainly to avoid concurrent accesses to Redis' database
    with RED.lock(lock_name):
        if not RED.exists(sem_name):
            # This is the first time we try to run this task
            #
            # Initialise a (key, value) pair in Redis with
            # key = ``sem_name``
            # value = "number of children of the task"
            #
            # ``value`` will be decremented each time one of the
            # dependency of the given task will be run
            if task.dependencies:
                RED.set(sem_name, len(task.dependencies))
            else:
                RED.set(sem_name, 1)

        RED.decr(sem_name)
        # This way, if (value == 0) the task's last dependency just
        # ended and we can run the task's itself
        if int(RED.get(sem_name)):
            # If the value associated to ``sem_name`` in the database
            # is not 0 the task either is not ready (some dependencies
            # haven't been run) or it has already been run (for
            # whatever reason) and we don't want to do it again
            # This last part is mainly defensive
            return
        else:
            # Time to actually run the task
            for command in task.command.split(';'):
                # Each part of the task's command is run one after
                # the other, this way we can identify which part
                # failed if appropriate

                print "'%s' '%s'" % (task.target, command)
                ret_code = system(command)
                if ret_code != 0:
                    raise RuntimeError("'%s' failed with code '%s'" %
                                       (command, ret_code))
            print "done '%s'" % task.target

            # Launch all the task's dependencies in parrallel
            group((run_task.s(child) for child in task.children))()

    # The task was run at this point
    with RED.lock(SLAVE_LOCK):
        # Decrement the number of task to run
        RED.decr(TASK_NUM)
        if not int(RED.get(TASK_NUM)):
            # There are no task to run anymore
            # Set the end time
            RED.set(END_TIME, time())
            # Push something on the ``END_LIST`` so the master can return
            RED.rpush(END_LIST, 0)

