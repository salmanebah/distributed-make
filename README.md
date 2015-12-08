# distributed-make
A distributed make using celery for task distribution.
## Local installation ubuntu 14.04
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

## Running locally
Assuming the following directory structure:
```
- src
  - celeryconfig.py
  - makeparse.py
  - master.py
  - result.py
  - work.py
  - Makefile
  - premier.c
  - premier
```
1. Create ```master_node``` with ```localhost``` as the content
2. Start ```celery``` 
```sh
celery worker -A work -linfo 
```
2. Launch the main program with:
```sh
python master.py -f Master premier
```

## Deploying on Grid'5000
1. Reserve nodes on Grid'5000 with the script `reserve.sh` in `deploy` directory:
```sh
./reserve.sh 4 1:30:00
```
2. Automatically provision the nodes with the script `deploy.sh` in `deploy` directory
```sh
./deploy.sh
```

This will create two files `master_node` and `worker_nodes` with respectively the
addresses of the machines acting as the master and the workers.


## Running on Grid'5000
Running the program on Grid'5000 **assumes the deployment described earlier**.

**NOTE:** The program uses `nfs` to share files between the nodes

Assuming the following directory structure:
```
- src
  - celeryconfig.py
  - makeparse.py
  - master.py
  - result.py
  - work.py
  - Makefile
  - premier.c
  - premier
  - master_node
  - worker_nodes
```
1. Start ```celery``` for all ```worker-node``` in ```worker_nodes```
```sh
ssh root@worker-node
celery worker -A work -linfo 
```
2. Launch the main program with:
```sh
python master.py -f Master premier
```
