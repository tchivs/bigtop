# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class bigtop_toolchain::user {

  user { 'jenkins':
    ensure => present,
    home => '/var/lib/jenkins',
    managehome => true,
    uid        => 2000,
    gid        => 'jenkins',
    require    => Group['jenkins'],
  }

  group { 'jenkins':
    ensure => present,
    gid    => 2000,
  }

  file {"/var/lib/jenkins/.m2":
    ensure => directory,
    owner => 'jenkins',
    group => 'jenkins',
    mode => "755",
    require => User['jenkins'],
  }

  file {"/var/lib/jenkins/.ssh":
    ensure => directory,
    owner => 'jenkins',
    group => 'jenkins',
    mode => "600",
    require => User['jenkins'],
  }
}
