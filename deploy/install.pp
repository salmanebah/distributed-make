# python 2.7
# pip
# celery
# start celery exec on workers
# start worker.py on workers
# start master and listener on master
# use a service to start celery on worker
# put celery bin in /etc/init.d/celery before

package { 'python':
  ensure => present,
  name   => 'python'
}

package { 'pip':
  ensure  => present,
  name    => 'python-pip',
  require => Package['python']
}

exec { 'celery':
  cwd     => '/tmp',
  command => 'pip install celery',
  require => Package['pip'],
  path    => ['/usr/bin', 'usr/local/bin']
}
