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

file { 'rabbitmq-conf':
  ensure  => present,
  notify  => Service['rabbitmq-service'],
  path    => '/etc/rabbitmq/rabbitmq.config',
  content => "[{rabbit, [{loopback_users, []}]}].\n",
  require => Package['rabbitmq']
}

exec { 'redis-conf':
  cwd     => '/etc/redis',
  notify  => Service['redis-service'],
  command => 'sed -i \'/bind 127.0.0.1/c\# bind 127.0.0.1\' redis.conf',
  require => Package['redis'],
  path    => ['/bin', '/usr/bin', 'usr/local/bin']
}

service { 'rabbitmq-service':
  ensure  => running,
  name    => 'rabbitmq-server',
  require => File['rabbitmq-conf'],
}

service { 'redis-service':
  ensure  => running,
  name    => 'redis-server',
  require => Package['redis-server']
}


package {'blender':
  ensure => present,
  name   => 'blender'
}

package {'imagemagick':
  ensure => present,
  name   => 'imagemagick'
}

package {'bc':
  ensure => present,
  name   => 'bc'
}

package { 'ffmpeg':
  ensure => present,
  name   => 'ffmpeg'
}

exec { 'unzip-update':
  command => 'apt-get update',
  path    => ['/usr/bin', 'usr/local/bin']
}

package { 'unzip':
  ensure  => present,
  name    => 'unzip',
  require => Exec['unzip-update']
}
