# distributed-make
A distributed make using celery for task distribution.

1. [Local installation](#local-install)
2. [Running locally](#run-local)
3. [Deploying on Grid'5000](#dep-g5k)
4. [Running on Grid'5000](#run-g5k)
5. [Makefile options](#make-opt)

<a name="local-install"></a>
## Local installation ubuntu 14.04
- Install puppet: 
```sh
sudo apt-get install puppet
```
- Install puppetlabs-apt: 
```sh
sudo puppet module install --modulepath=/usr/share/puppet/modules puppetlabs-apt
```
- Apply the puppet manifest in ```deploy```
```sh
sudo puppet apply local_intall.pp
```

<a name="run-local"></a>
## Running locally 
Assuming the following directory structure:
```
- src
  - celeryconfig.py
  - makeparse.py
  - logging.ini
  - master.py
  - result.py
  - work.py
  - Makefile
  - premier.c
```
- Create ```master_node``` with ```localhost``` as the content
- Start ```celery``` 
```sh
celery worker -A work -l info 
```
- Launch the main program with:
```sh
python master.py -f Makefile premier
```
<a name="dep-g5k"></a>
## Deploying on Grid'5000 
- Reserve nodes on Grid'5000 with the script `reserve.sh` in `deploy` directory.
```sh
./reserve.sh 4 1:30:00
```
for example, the commande below reserves ```4 nodes for 1h30```:
- Automatically provision the nodes with the script `deploy.sh` in `deploy` directory
```sh
./deploy.sh
```

This will create two files `master_node` and `worker_nodes` with respectively the
addresses of the machines acting as the master and the workers.

<a name="run-g5k"></a>
## Running on Grid'5000 
Running the program on Grid'5000 **assumes the deployment described earlier**.

**NOTE:** The program uses `nfs` to share files between the nodes

Assuming the following directory structure:
```
- src
  - celeryconfig.py
  - makeparse.py
  - logging.ini
  - master.py
  - result.py
  - work.py
  - Makefile
  - premier.c
  - master_node
  - worker_nodes
```
- Start ```celery``` for all ```worker-node``` in ```worker_nodes```
```sh
ssh root@worker-node
celery worker -A work -linfo 
```
- Launch the main program with:
```sh
python master.py -f Makefile premier
```
<a name="make-opt"></a>
## Makefile options 
```sh
python master.py -h
```
displays the ```master.py``` command line option. By default, running ```python master.py``` without the ```-f``` switch will use ```GNU-Makefile``` or ```makefile``` or ```Makefile``` found in the current directory and will execute the first target in the ```makefile```. The `-a` or ```--async``` option allows to run asynchronously all the tasks without blocking the ```master``` otherwise it will wait for the last task's completion. 
