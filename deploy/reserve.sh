#! /usr/bin/env bash

oarsub  -l nodes=$1,walltime=$2 -t deploy /home/sbah/public/dmake/deploy.sh
