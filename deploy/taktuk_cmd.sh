#! /usr/bin/env bash

if [ $# -lt 1 ]
then
    printf 'help: %s <puppet_manifest> ' $(basename $0)
    exit 1
fi

export http_proxy="http://proxy:3128"
export https_proxy="http://proxy:3128"
apt-get --yes install  puppet
puppet apply $1
