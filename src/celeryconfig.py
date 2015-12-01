# -*- coding: utf-8 -*-
#

import os

with open("master_node", 'r') as stream:
    master_node = stream.read().strip()

# Broker
BROKER_URL = "amqp://" + master_node

# Backend
CELERY_RESULT_BACKEND = "redis://" + master_node + "/1"
