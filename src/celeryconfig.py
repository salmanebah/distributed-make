# -*- coding: utf-8 -*-
#

import os

with open("master_node", 'r') as stream:
    MASTER_NODE = stream.read().strip()

# Broker
BROKER_URL = "amqp://" + MASTER_NODE

# Backend
CELERY_RESULT_BACKEND = "redis://" + MASTER_NODE + "/1"
