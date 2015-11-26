# start celery as service on worker nodes

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
  command => 'pip install -U celery[redis]',
  require => Package['pip'],
  path    => ['/usr/bin', 'usr/local/bin']
}

package {'rabbitmq':
  ensure => present,
  name   => 'rabbitmq-server',
}

package {'redis':
  ensure => present,
  name   => 'redis-server'
}

service { 'rabbitmq-service':
  ensure  => running,
  name    => 'rabbitmq-server',
  require => Package['rabbitmq']
}

service { 'redis-service':
  ensure  => running,
  name    => 'redis-server',
  require => Package['redis-server']
}
