#! /usr/bin/env bash

export http_proxy="http://proxy:3128"
export https_proxy="http://proxy:3128"
apt-get --yes install  puppet
puppet apply /home/sbah/public/dmake/install.pp
