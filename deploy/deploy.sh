#! /usr/bin/env bash

if [ $# -lt 2 ]
then
    printf 'help: %s <taktuk_script> <puppet_manifest> ' $(basename $0)
    exit 1
fi
#get the master node
uniq $OAR_NODE_FILE | head -n 1 > master_node
# get the workers node
uniq $OAR_NODE_FILE | tail -n +2 > worker_nodes

# deploy
kadeploy3 -f $OAR_NODE_FILE -e jessie-x64-nfs -k

# install puppet on nodes and execute recipes
taktuk -l root -s -f $OAR_NODE_FILE broadcast exec [ $1 $2 ]
