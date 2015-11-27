# -*- coding: utf-8 -*-
#
# this file is part of the SDCA Project (team 11)
#

from celery import Celery, group
from celery.utils.log import get_task_logger
from logging import INFO
from os import system
from Parser import Task
from redis import Redis
from time import sleep

app = Celery('Work', backend="redis://localhost", broker='amqp://localhost')

logger = get_task_logger(__name__)
logger.setLevel(INFO)

red = Redis()

@app.task(name="Work.run_task", ignore_result=False)
def run_task(task):
    """
    Runs a task
    """
    lock_name = task.target + "_lock"
    sem_name = task.target + "_sem"
    with red.lock(lock_name):
        if not red.exists(sem_name):
            initial_val = len(task.dependencies)
            if initial_val == 0:
                initial_val = 1
            red.set(sem_name, initial_val)
        red.decr(sem_name)
        if int(red.get(sem_name)):
            return
        else:
            for command in task.command.split(';'):
                print "'%s' '%s'" % (task.target, command)
                ret_code = system(command)
                if ret_code != 0:
                    raise RuntimeError("'%s' failed with code '%s'" %
                                       (command, ret_code))
            print "done '%s'" % task.target
            group((run_task.s(child) for child in task.children))()

