# -*- coding: utf-8 -*-
#
# this file is part of the SDCA Project (team 11)
#

from celery import Celery, group
from celeryconfig import MASTER_NODE
from celery.signals import task_postrun
from celery.utils.log import get_task_logger
from logging import INFO
from os import system
from makeparse import Task
from redis import Redis
from time import time

app = Celery()
app.config_from_object('celeryconfig')

logger = get_task_logger(__name__)
logger.setLevel(INFO)

START_TIME = "start_time"
END_TIME = "end_time"

RED = Redis(host=MASTER_NODE)

@task_postrun.connect()
def close_timestamp(**kwargs):
    RED.set(END_TIME, time())

@app.task
def run_task(task):
    """
    Runs a task
    """
    lock_name = task.target + "_lock"
    sem_name = task.target + "_sem"
    with RED.lock(lock_name):
        if not RED.exists(sem_name):
            initial_val = len(task.dependencies)
            if initial_val == 0:
                initial_val = 1
            RED.set(sem_name, initial_val)
        RED.decr(sem_name)
        if int(RED.get(sem_name)):
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

