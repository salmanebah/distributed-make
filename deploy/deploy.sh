#! /usr/bin/env bash

#get the master node
uniq $OAR_NODE_FILE | head -n 1 > master_node
# get the workers node
uniq $OAR_NODE_FILE | tail -n +2 > worker_nodes

# deploy
kadeploy3 -f $OAR_NODE_FILE -e wheezy-x64-nfs -k

# install puppet on nodes and execute recipes
taktuk -l root -s -f $OAR_NODE_FILE broadcast exec [ /home/sbah/public/dmake/taktuk_cmd.sh ]
