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

%define etc_default %{parent_dir}/etc/default
%define zookeeper_name zookeeper
%define zookeeper_pkg_name zookeeper%{pkg_name_suffix}

%define usr_lib_zookeeper %{parent_dir}/usr/lib/%{zookeeper_name}
%define var_lib_zookeeper %{parent_dir}/var/lib/%{zookeeper_name}
%define etc_zookeeper_conf_dist %{parent_dir}/etc/zookeeper/conf.dist

%define bin_dir %{parent_dir}/%{_bindir}
%define man_dir %{parent_dir}/%{_mandir}
%define doc_dir %{parent_dir}/%{_docdir}
%define include_dir %{parent_dir}/%{_includedir}
%define lib_dir %{parent_dir}/%{_libdir}

# No prefix directory
%define np_var_log_zookeeper /var/log/%{zookeeper_name}
%define np_run_zookeeper /run/%{zookeeper_name}
%define np_etc_zookeeper /etc/%{zookeeper_name}

%define svc_zookeeper %{zookeeper_name}-server
%define svc_zookeeper_rest %{zookeeper_name}-rest

%if  %{?suse_version:1}0

# Only tested on openSUSE 11.4. let's update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# SLES is more strict anc check all symlinks point to valid path
# But we do point to a hadoop jar which is not there at build time
# (but would be at install time).
# Since our package build system does not handle dependencies,
# these symlink checks are deactivated
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}


%define doc_zookeeper %{doc_dir}/%{zookeeper_name}
%define alternatives_cmd update-alternatives
%define alternatives_dep update-alternatives
%define chkconfig_dep    aaa_base
%define service_dep      aaa_base
%global initd_dir %{_sysconfdir}/rc.d

%else

%define doc_zookeeper %{doc_dir}/%{zookeeper_name}-%{zookeeper_version}
%define alternatives_cmd alternatives
%define alternatives_dep chkconfig 
%define chkconfig_dep    chkconfig
%define service_dep      initscripts
%global initd_dir %{_sysconfdir}/rc.d/init.d

%endif



Name: %{zookeeper_pkg_name}
Version: %{zookeeper_version}
Release: %{zookeeper_release}
Summary: A high-performance coordination service for distributed applications.
URL: http://zookeeper.apache.org/
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
License: ASL 2.0
Source0: apache-%{zookeeper_name}-%{zookeeper_base_version}.tar.gz
Source1: do-component-build
Source2: install_zookeeper.sh
Source5: zookeeper.1
Source6: zoo.cfg
Source7: zookeeper.default
Source8: init.d.tmpl
Source9: zookeeper-rest.svc
Source10: %{svc_zookeeper}.service
Source11: %{svc_zookeeper}.tmpfile
#BIGTOP_PATCH_FILES
BuildRequires: autoconf, automake, cppunit-devel, systemd

%if 0%{?openEuler} == 0
BuildRequires: systemd-rpm-macros
%endif

Requires(pre): coreutils, /usr/sbin/groupadd, /usr/sbin/useradd
Requires(post): %{alternatives_dep}
Requires(preun): %{alternatives_dep}
Requires: bigtop-utils >= 0.7

%description 
ZooKeeper is a centralized service for maintaining configuration information, 
naming, providing distributed synchronization, and providing group services. 
All of these kinds of services are used in some form or another by distributed 
applications. Each time they are implemented there is a lot of work that goes 
into fixing the bugs and race conditions that are inevitable. Because of the 
difficulty of implementing these kinds of services, applications initially 
usually skimp on them ,which make them brittle in the presence of change and 
difficult to manage. Even when done correctly, different implementations of these services lead to management complexity when the applications are deployed.  

%package server
Summary: The Hadoop Zookeeper server
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(post): %{chkconfig_dep}
Requires(preun): %{service_dep}, %{chkconfig_dep}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%endif

%if  0%{?mgaversion}
# Required for init scripts
Requires: initscripts
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
# Required for init scripts
%if 0%{?fedora} >= 40
Requires: redhat-lsb-core
%else
Requires: /lib/lsb/init-functions
%endif
%endif


%description server
This package starts the zookeeper server on startup

%package rest
Summary: ZooKeeper REST Server
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(post): %{chkconfig_dep}
Requires(preun): %{service_dep}, %{chkconfig_dep}

%package native
Summary: C bindings for ZooKeeper clients
Group: Development/Libraries

%description native
Provides native libraries and development headers for C / C++ ZooKeeper clients. Consists of both single-threaded and multi-threaded implementations.

%description rest
This package starts the zookeeper REST server on startup

%prep
%setup -n apache-%{zookeeper_name}-%{zookeeper_base_version}

#BIGTOP_PATCH_COMMANDS

%build
bash %{SOURCE1}

%install
%__rm -rf $RPM_BUILD_ROOT
cp $RPM_SOURCE_DIR/zookeeper.1 $RPM_SOURCE_DIR/zoo.cfg $RPM_SOURCE_DIR/zookeeper.default .
bash %{SOURCE2} \
          --build-dir=build \
          --prefix=$RPM_BUILD_ROOT \
          --doc-dir=%{doc_zookeeper} \
          --lib-dir=%{usr_lib_zookeeper} \
          --bin-dir=%{bin_dir} \
          --man-dir=%{man_dir} \
          --conf-dist-dir=%{etc_zookeeper_conf_dist} \
          --etc-default=%{etc_default} \
          --system-include-dir=%{include_dir} \
          --system-lib-dir=%{lib_dir}


    
# Install Zookeeper REST server init script
init_file=$RPM_BUILD_ROOT/%{initd_dir}/zookeeper-rest
bash $RPM_SOURCE_DIR/init.d.tmpl $RPM_SOURCE_DIR/zookeeper-rest.svc rpm $init_file

# Install ZooKeeper Server systemd service file
%__install -D -m 0644 %{SOURCE10} $RPM_BUILD_ROOT/%{_unitdir}/%{svc_zookeeper}.service

# Install ZooKeeper Server systemd-tmpfile file
%__install -D -m 0644 %{SOURCE11} $RPM_BUILD_ROOT/%{_tmpfilesdir}/%{svc_zookeeper}.conf

%pre
getent group zookeeper >/dev/null || groupadd -r zookeeper
getent passwd zookeeper > /dev/null || useradd -c "ZooKeeper" -s /sbin/nologin -g zookeeper -r -d %{var_lib_zookeeper} zookeeper 2> /dev/null || :

%__install -d -o zookeeper -g zookeeper -m 0755 %{np_run_zookeeper}
%__install -d -o zookeeper -g zookeeper -m 0755 %{np_var_log_zookeeper}

# Manage configuration symlink
%post
%{alternatives_cmd} --install %{np_etc_zookeeper}/conf %{zookeeper_name}-conf %{etc_zookeeper_conf_dist} 30
%__install -d -o zookeeper -g zookeeper -m 0755 %{var_lib_zookeeper}


%preun
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove %{zookeeper_name}-conf %{etc_zookeeper_conf_dist} || :
fi


%post server
chkconfig --add %{svc_zookeeper}
%systemd_post zookeeper-server.service

%preun server
if [ $1 = 0 ] ; then
	service %{svc_zookeeper} stop > /dev/null 2>&1
	chkconfig --del %{svc_zookeeper}
fi
%systemd_preun zookeeper-server.service

%postun server
if [ $1 -ge 1 ]; then
        service %{svc_zookeeper} condrestart > /dev/null 2>&1
fi
%systemd_postun zookeeper-server.service

%post rest
	chkconfig --add %{svc_zookeeper_rest}

%preun rest
if [ $1 = 0 ] ; then
	service %{svc_zookeeper_rest} stop > /dev/null 2>&1
	chkconfig --del %{svc_zookeeper_rest}
fi

%postun rest
if [ $1 -ge 1 ]; then
        service %{svc_zookeeper_rest} condrestart > /dev/null 2>&1
fi

#######################
#### FILES SECTION ####
#######################
%files
%defattr(-,root,root)
%config(noreplace) %{etc_zookeeper_conf_dist}
%config(noreplace) %{etc_default}/%{zookeeper_name}
%{np_etc_zookeeper}
%{usr_lib_zookeeper}
%{bin_dir}/zookeeper-server
%{bin_dir}/zookeeper-server-initialize
%{bin_dir}/zookeeper-client
%{bin_dir}/zookeeper-server-cleanup
%doc %{doc_zookeeper}
%{man_dir}/man1/zookeeper.1.*

%files server
%attr(0644,root,root) %{_unitdir}/zookeeper-server.service
%attr(0644,root,root) %{_tmpfilesdir}/zookeeper-server.conf

%files rest
%attr(0755,root,root) %{initd_dir}/%{svc_zookeeper_rest}

%files native
%defattr(-,root,root)
%{usr_lib_zookeeper}-native
%{bin_dir}/cli_*
%{bin_dir}/load_gen*
%{include_dir}/zookeeper
%{lib_dir}/*

