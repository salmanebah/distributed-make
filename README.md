# distributed-make
A distributed make using celery for task distribution.
## Local installation ubuntu 14.04
The program requires puppet to automatically install the packages:
1. install puppet:
```sh
sudo apt-get install puppet
```
2. install puppetlabs-apt:
```sh
sudo puppet module install --modulepath=/usr/share/puppet/modules puppetlabs-apt
```
3. apply the puppet manifest
```sh
sudo puppet apply local_intall.pp
```
## Deploying on Grid'5000
1. Reserve nodes on Grid'5000 with the script `reserve.sh` in `deploy` directory
2. Provision the nodes with the script `deploy.sh` in `deploy`
## Running on locally


## Running on Grid'5000
