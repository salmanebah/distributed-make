# -*- coding: utf-8 -*-
#

"""
This file is used by this package to configure both the master
and the slave processes
"""

with open("master_node", 'r') as stream:
    MASTER_NODE = stream.read().strip()

# Broker
BROKER_URL = "amqp://" + MASTER_NODE

# Backend
CELERY_RESULT_BACKEND = "redis://" + MASTER_NODE + "/1"
