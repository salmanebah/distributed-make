#! /usr/bin/env bash

PWD="`(cd $(dirname \"$0\") && pwd )`"
TAKTUK="${PWD}/taktuk_cmd.sh"
MANIFEST="${PWD}/install.pp"

#get the master node
uniq $OAR_NODE_FILE | head -n 1 > master_node
# get the workers node
uniq $OAR_NODE_FILE | tail -n +2 > worker_nodes

# deploy
kadeploy3 -f $OAR_NODE_FILE -e jessie-x64-nfs -k

# install puppet on nodes and execute recipes
taktuk -l root -s -f $OAR_NODE_FILE broadcast exec [ $TAKTUK $MANIFEST ]
