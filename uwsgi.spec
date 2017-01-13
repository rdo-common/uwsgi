# Version
%global majornumber 2
%global minornumber 0
%global releasenumber 14

# Documentation sources:
%global commit f6eacc586fda4aedf83ed29aea38087dff8f50f2
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global docrepo uwsgi-docs
%{!?_httpd_apxs: %{expand: %%global _httpd_apxs %%{_sbindir}/apxs}}
%{!?_httpd_moddir:    %{expand: %%global _httpd_moddir    %%{_libdir}/httpd/modules}}

# This is primarily built for fedora, make it easy right now
%if 0%{?fedora}
%bcond_without systemd
%bcond_without go
%bcond_without python3
%bcond_without tornado3
%{!?python3_pkgversion: %global python3_pkgversion 3}
%bcond_without ruby19
%bcond_without tuntap
%bcond_without zeromq
%bcond_without greenlet
%bcond_without perl
%bcond_without glusterfs
%bcond_without java
#mono
%ifnarch %{mono_arches}
%bcond_with mono
%else
%bcond_without mono
%endif
# mongodblibs
# mongodb is little endian only
%ifnarch ppc ppc64 s390 s390x
%bcond_without mongodblibs
%else
%bcond_with mongodblibs
%endif
# v8
%ifnarch %{ix86} x86_64 %{arm}
%bcond_with v8
%else
%bcond_without v8
%endif
#mongodblibs dependency
%if %{without mongodblibs}
%bcond_with gridfs
%else
%bcond_without gridfs
%endif
#Fedora endif
%endif

# Conditionally disable some things in epel6
%if 0%{?rhel} == 6
# el6 ppc64 doesn't hava java
%ifarch ppc64
%bcond_with java
%else
%bcond_without java
%endif
# el6 doesn't ship with systemd
%bcond_with systemd
# el6 doesn't have go
%bcond_with go
# el6 doesn't have python3
%bcond_with python3
%bcond_with tornado3
# el6 ships with ruby 1.8 but fiberloop/rbthreads needs 1.9
%bcond_with ruby19
# el6 doesn't have perl-PSGI
# el6 does have perl-Coro
%bcond_with perl
# this fails in el not sure why
%bcond_with gridfs
%bcond_with tuntap
%bcond_with mongodblibs
%global manual_py_compile 0
%else
%global manual_py_compile 1
%endif

# Conditionally enable/disable some things in epel7
%if 0%{?rhel} == 7
# el7 does have java
%bcond_without java
# el7 does have systemd
%bcond_without systemd
# el7 does have python3
%bcond_without python3
%{!?python3_pkgversion: %global python3_pkgversion 34}
# ...but no python3-tornado yet
%bcond_with tornado3
# el7 doesn't have zeromq
%bcond_with zeromq
# el7 doesn't have greenlet
%bcond_with greenlet
# el7 does have perl-PSGI
# el7 doesn't have perl-Coro
%bcond_without perl
# el7 can now build glusterfs but only on x86_64
%ifnarch x86_64
%bcond_with glusterfs
%else
%bcond_without glusterfs
%endif
# this fails in el7 not sure why
%bcond_with gridfs
%endif

# Turn off byte compilation so it doesn't try
# to auto-optimize the code in /usr/src/uwsgi
%if %{manual_py_compile} == 1
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%endif

Name:           uwsgi
Version:        %{majornumber}.%{minornumber}.%{releasenumber}
Release:        6%{?dist}
Summary:        Fast, self-healing, application container server
Group:          System Environment/Daemons
License:        GPLv2 with exceptions
URL:            https://github.com/unbit/uwsgi
Source0:        http://projects.unbit.it/downloads/%{name}-%{version}.tar.gz
Source1:        fedora.ini
Source2:        uwsgi.service
Source3:        emperor.ini
Source4:        https://github.com/unbit/%{docrepo}/archive/%{commit}/%{docrepo}-%{shortcommit}.tar.gz
Source5:        README.Fedora
Source6:        uwsgi.init
Patch0:         uwsgi_trick_chroot_rpmbuild.patch
Patch1:         uwsgi_fix_rpath.patch
Patch2:         uwsgi_ruby20_compatibility.patch
Patch3:         uwsgi_fix_lua.patch
# https://github.com/unbit/uwsgi/issues/882
Patch5:         uwsgi_fix_mongodb.patch
Patch6:         uwsgi_v8-314_compatibility.patch
BuildRequires:  curl,  python2-devel, libxml2-devel, libuuid-devel, jansson-devel
BuildRequires:  libyaml-devel, ruby-devel
%if %{with python3}
BuildRequires:  python%{python3_pkgversion}-devel
%endif
%if %{with greenlet}
BuildRequires:  python-greenlet-devel
%endif
%if %{with glusterfs}
BuildRequires:  glusterfs-devel, glusterfs-api-devel
%endif
BuildRequires:  lua-devel, ruby, pcre-devel
BuildRequires:  php-devel, php-embedded, libedit-devel, krb5-devel
%if 0%{?fedora} >= 26
BuildRequires:  compat-openssl10-devel
%else
BuildRequires:  openssl-devel
%endif
BuildRequires:  bzip2-devel, gmp-devel, pam-devel
BuildRequires:  java-devel, sqlite-devel, libcap-devel
BuildRequires:  httpd-devel, tcp_wrappers-devel, libcurl-devel
BuildRequires:  gloox-devel, libstdc++-devel
BuildRequires:  GeoIP-devel, libevent-devel, zlib-devel
BuildRequires:  openldap-devel, boost-devel
BuildRequires:  libattr-devel, libxslt-devel
%if %{with perl}
BuildRequires:  perl-devel, perl-ExtUtils-Embed
%if 0%{?fedora} >= 15
BuildRequires:  perl-Coro
%endif
%endif
%if %{with zeromq}
BuildRequires:  zeromq-devel
%endif
%if %{with go}
BuildRequires:  libgo-devel, gcc-go
%endif
%if %{with systemd}
BuildRequires:  systemd-devel, systemd-units
%endif
%if %{with mono}
BuildRequires:  mono-devel, mono-web
%endif
%if %{with v8}
%if 0%{?fedora} >= 25
BuildRequires:  v8-314-devel
%else
BuildRequires:  v8-devel
%endif
%endif
%if %{with mongodblibs}
BuildRequires:  libmongodb-devel
%endif

Obsoletes:      %{name}-loggers <= 1.9.8-1
Obsoletes:      %{name}-routers <= 2.0.6
Obsoletes:      %{name}-plugin-erlang <= 1.9.20-1
Obsoletes:      %{name}-plugin-admin <= 2.0.6

Requires(pre):    shadow-utils
%if %{with systemd}
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

%filter_requires_in %{_usrsrc}
%filter_provides_in %{_usrsrc}
%filter_setup

%description
uWSGI is a fast (pure C), self-healing, developer/sysadmin-friendly
application container server.  Born as a WSGI-only server, over time it has
evolved in a complete stack for networked/clustered web applications,
implementing message/object passing, caching, RPC and process management.
It uses the uwsgi (all lowercase, already included by default in the Nginx
and Cherokee releases) protocol for all the networking/interprocess
communications.  Can be run in preforking mode, threaded,
asynchronous/evented and supports various form of green threads/co-routine
(like uGreen and Fiber).  Sysadmin will love it as it can be configured via
command line, environment variables, xml, .ini and yaml files and via LDAP.
Being fully modular can use tons of different technology on top of the same
core.

%package -n %{name}-devel
Summary:    uWSGI - Development header files and libraries
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description -n %{name}-devel
This package contains the development header files and libraries
for uWSGI extensions

%package -n python-uwsgidecorators
Summary:        Python decorators providing access to the uwsgi API
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-plugin-python = %{version}-%{release}

%description -n python-uwsgidecorators
The uwsgidecorators Python module provides higher-level access to the uWSGI API.

%package -n python3-uwsgidecorators
Summary:        Python 3 decorators providing access to the uwsgi API
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-plugin-python3 = %{version}-%{release}

%description -n python3-uwsgidecorators
The uwsgidecorators Python 3 module provides higher-level access to the uWSGI API.

%package -n %{name}-docs
Summary:  uWSGI - Documentation
Group:    Documentation
Requires: %{name}

%description -n %{name}-docs
This package contains the documentation files for uWSGI

%package -n %{name}-plugin-common
Summary:  uWSGI - Common plugins for uWSGI
Group:    System Environment/Daemons
Requires: %{name} = %{version}-%{release}

%description -n %{name}-plugin-common
This package contains the most common plugins used with uWSGI. The
plugins included in this package are: cache, CGI, RPC, uGreen

# Stats pushers

%package -n %{name}-stats-pusher-file
Summary:    uWSGI - File Stats Pusher for uWSGI
Requires:   %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-stats-pusher-file
This package contains the stats_pusher_file plugin for uWSGI

%if %{with mongodblibs}
%package -n %{name}-stats-pusher-mongodb
Summary:    uWSGI - MongoDB Stats Pusher for uWSGI
Requires:   %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-stats-pusher-mongodb
This package contains the stats_pusher_mongodb plugin for uWSGI
%endif

%package -n %{name}-stats-pusher-socket
Summary:    uWSGI - Socket Stats Pusher for uWSGI
Requires:   %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-stats-pusher-socket
This package contains the stats_pusher_socket plugin for uWSGI

%package -n %{name}-stats-pusher-statsd
Summary:    uWSGI - StatsD Stats Pusher for uWSGI
Requires:   %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-stats-pusher-statsd
This package contains the stats_pusher_statsd plugin for uWSGI

%package -n %{name}-stats-pusher-zabbix
Summary:    uWSGI - Zabbix Stats Pusher for uWSGI
Requires:   %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-stats-pusher-zabbix
This package contains the zabbix plugin for uWSGI

# Alarms

%package -n %{name}-alarm-curl
Summary:  uWSGI - Curl alarm plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libcurl

%description -n %{name}-alarm-curl
This package contains the alarm_curl alarm plugin for uWSGI

%package -n %{name}-alarm-xmpp
Summary:  uWSGI - Curl alarm plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, gloox

%description -n %{name}-alarm-xmpp
This package contains the alarm_xmpp alarm plugin for uWSGI

# Transformations

%package -n %{name}-transformation-chunked
Summary:  uWSGI - Chunked Transformation plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-router-uwsgi = %{version}-%{release}

%description -n %{name}-transformation-chunked
This package contains the transformation_chunked plugin for uWSGI

%package -n %{name}-transformation-gzip
Summary:  uWSGI - GZip Transformation plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-router-uwsgi = %{version}-%{release}

%description -n %{name}-transformation-gzip
This package contains the transformation_gzip plugin for uWSGI

%package -n %{name}-transformation-offload
Summary:  uWSGI - Off-Load Transformation plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-router-uwsgi = %{version}-%{release}

%description -n %{name}-transformation-offload
This package contains the transformation_offload plugin for uWSGI

%package -n %{name}-transformation-template
Summary:  uWSGI - Template Transformation plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-router-uwsgi = %{version}-%{release}

%description -n %{name}-transformation-template
This package contains the transformation_template plugin for uWSGI

%package -n %{name}-transformation-tofile
Summary:  uWSGI - ToFile Transformation plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-router-uwsgi = %{version}-%{release}

%description -n %{name}-transformation-tofile
This package contains the transformation_tofile plugin for uWSGI

%package -n %{name}-transformation-toupper
Summary:  uWSGI - ToUpper Transformation plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-transformation-toupper
This package contains the transformation_toupper plugin for uWSGI

# Loggers

%package -n %{name}-log-encoder-msgpack
Summary:  uWSGI - msgpack log encoder plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-log-encoder-msgpack
This package contains the msgpack log encoder plugin for uWSGI

%package -n %{name}-logger-crypto
Summary:  uWSGI - logcrypto logger plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-logger-crypto
This package contains the logcrypto logger plugin for uWSGI

%package -n %{name}-logger-file
Summary:   uWSGI - logfile logger plugin
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-loggers <= 1.9.8-1
Provides:  %{name}-loggers = %{version}-%{release}

%description -n %{name}-logger-file
This package contains the logfile logger plugin for uWSGI

%package -n %{name}-logger-graylog2
Summary:   uWSGI - Graylog2 logger plugin
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}, zlib

%description -n %{name}-logger-graylog2
This package contains the graylog2 logger plugin for uWSGI

%if %{with mongodblibs}
%package -n %{name}-logger-mongodb
Summary:   uWSGI - mongodblog logger plugin
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-loggers <= 1.9.8-1
Provides:  %{name}-loggers = %{version}-%{release}

%description -n %{name}-logger-mongodb
This package contains the mongodblog logger plugin for uWSGI
%endif

%package -n %{name}-logger-pipe
Summary:  uWSGI - logpipe logger plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-logger-pipe
This package contains the logcrypto logger plugin for uWSGI

%package -n %{name}-logger-redis
Summary:   uWSGI - redislog logger plugin
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-loggers <= 1.9.8-1
Provides:  %{name}-loggers = %{version}-%{release}

%description -n %{name}-logger-redis
This package contains the redislog logger plugin for uWSGI

%package -n %{name}-logger-rsyslog
Summary:   uWSGI - rsyslog logger plugin
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-plugin-rsyslog <= 1.9.8-1
Provides:  %{name}-plugin-rsyslog = %{version}-%{release}

%description -n %{name}-logger-rsyslog
This package contains the rsyslog logger plugin for uWSGI

%package -n %{name}-logger-socket
Summary:   uWSGI - logsocket logger plugin
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-loggers <= 1.9.8-1
Provides:  %{name}-loggers = %{version}-%{release}

%description -n %{name}-logger-socket
This package contains the logsocket logger plugin for uWSGI

%package -n %{name}-logger-syslog
Summary:   uWSGI - syslog logger plugin
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-plugin-syslog <= 1.9.8-1
Provides:  %{name}-plugin-syslog = %{version}-%{release}

%description -n %{name}-logger-syslog
This package contains the syslog logger plugin for uWSGI

%if %{with systemd}
%package -n %{name}-logger-systemd
Summary:  uWSGI - systemd journal logger plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-logger-systemd
This package contains the systemd journal logger plugin for uWSGI
%endif

%if %{with zeromq}
%package -n %{name}-logger-zeromq
Summary:  uWSGI - ZeroMQ logger plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, zeromq

%description -n %{name}-logger-zeromq
This package contains the ZeroMQ logger plugin for uWSGI
%endif

# Plugins

%package -n %{name}-plugin-airbrake
Summary:  uWSGI - Plugin for AirBrake support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libcurl

%description -n %{name}-plugin-airbrake
This package contains the airbrake plugin for uWSGI

%package -n %{name}-plugin-cache
Summary:  uWSGI - Plugin for cache support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-cache
This package contains the cache plugin for uWSGI

%package -n %{name}-plugin-carbon
Summary:  uWSGI - Plugin for Carbon/Graphite support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-carbon
This package contains the Carbon plugin for uWSGI (to use in graphite)

%if %{with perl}
%package -n %{name}-plugin-psgi
Summary:  uWSGI - Plugin for PSGI support
Group:    System Environment/Daemons
Requires: perl-PSGI, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-psgi
This package contains the PSGI plugin for uWSGI

%if 0%{?fedora} >= 15
%package -n %{name}-plugin-coroae
Summary:  uWSGI - Plugin for PERL Coro support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-plugin-psgi = %{version}-%{release}, perl-Coro

%description -n %{name}-plugin-coroae
This package contains the coroae plugin for uWSGI
%endif
%endif

%package -n %{name}-plugin-cheaper-busyness
Summary:  uWSGI - Plugin for Cheaper Busyness algos
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-cheaper-busyness
This package contains the cheaper_busyness plugin for uWSGI

%package -n %{name}-plugin-cplusplus
Summary:  uWSGI - Plugin for C++ support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libstdc++

%description -n %{name}-plugin-cplusplus
This package contains the cplusplus plugin for uWSGI

%package -n %{name}-plugin-curl-cron
Summary:  uWSGI - Plugin for CURL Cron support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libcurl

%description -n %{name}-plugin-curl-cron
This package contains the curl_cron plugin for uWSGI

%package -n %{name}-plugin-dumbloop
Summary:  uWSGI - Plugin for Dumb Loop support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-dumbloop
This package contains the dumbloop plugin for uWSGI

%package -n %{name}-plugin-dummy
Summary:  uWSGI - Plugin for Dummy support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-dummy
This package contains the dummy plugin for uWSGI

%package -n %{name}-plugin-fiber
Summary:  uWSGI - Plugin for Ruby Fiber support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-plugin-rack = %{version}-%{release}

%description -n %{name}-plugin-fiber
This package contains the fiber plugin for uWSGI

%package -n %{name}-plugin-gccgo
Summary:  uWSGI - Plugin for GoLang support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libgo

%description -n %{name}-plugin-gccgo
This package contains the gccgo plugin for uWSGI

%package -n %{name}-plugin-geoip
Summary:  uWSGI - Plugin for GeoIP support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, GeoIP

%description -n %{name}-plugin-geoip
This package contains the geoip plugin for uWSGI

%package -n %{name}-plugin-gevent
Summary:  uWSGI - Plugin for GEvent support
Group:    System Environment/Daemons
Requires: %{name}-plugin-python = %{version}-%{release}, libevent

%description -n %{name}-plugin-gevent
This package contains the gevent plugin for uWSGI

%if %{with glusterfs}
%package -n %{name}-plugin-glusterfs
Summary:  uWSGI - Plugin for GlusterFS support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, glusterfs-api

%description -n %{name}-plugin-glusterfs
This package contains the glusterfs plugin for uWSGI
%endif

%if %{with greenlet}
%package -n %{name}-plugin-greenlet
Summary:  uWSGI - Plugin for Python Greenlet support
Group:    System Environment/Daemons
Requires: python-greenlet, %{name}-plugin-python = %{version}-%{release}

%description -n %{name}-plugin-greenlet
This package contains the python greenlet plugin for uWSGI
%endif

%if %{with gridfs}
%package -n %{name}-plugin-gridfs
Summary:  uWSGI - Plugin for GridFS support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libmongodb

%description -n %{name}-plugin-gridfs
This package contains the gridfs plugin for uWSGI
%endif

%if %{with java}
%package -n %{name}-plugin-jvm
Summary:  uWSGI - Plugin for JVM support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, java-headless, jpackage-utils

%description -n %{name}-plugin-jvm
This package contains the JVM plugin for uWSGI

%package -n %{name}-plugin-jwsgi
Summary:  uWSGI - Plugin for JWSGI support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-plugin-jvm = %{version}-%{release}

%description -n %{name}-plugin-jwsgi
This package contains the jwsgi plugin for uWSGI
%endif

%package -n %{name}-plugin-ldap
Summary:  uWSGI - Plugin for LDAP support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, openldap

%description -n %{name}-plugin-ldap
This package contains the ldap plugin for uWSGI

%package -n %{name}-plugin-lua
Summary:  uWSGI - Plugin for LUA support
Group:    System Environment/Daemons
Requires: lua, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-lua
This package contains the lua plugin for uWSGI

%if %{with zeromq}
%package -n %{name}-plugin-mongrel2
Summary:  uWSGI - Plugin for Mongrel2 support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, zeromq

%description -n %{name}-plugin-mongrel2
This package contains the mongrel2 plugin for uWSGI
%endif

%if %{with mono}
%package -n %{name}-plugin-mono
Summary:  uWSGI - Plugin for Mono / .NET support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, mono-web

%description -n %{name}-plugin-mono
This package contains the mono plugin for uWSGI
%endif

%package -n %{name}-plugin-nagios
Summary:  uWSGI - Plugin for Nagios support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-nagios
This package contains the nagios plugin for uWSGI

%package -n %{name}-plugin-notfound
Summary:  uWSGI - Plugin for notfound support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-notfound
This package contains the notfound plugin for uWSGI

%package -n %{name}-plugin-pam
Summary:  uWSGI - Plugin for PAM support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, pam

%description -n %{name}-plugin-pam
This package contains the PAM plugin for uWSGI

%package -n %{name}-plugin-php
Summary:  uWSGI - Plugin for PHP support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-php
This package contains the PHP plugin for uWSGI

%package -n %{name}-plugin-pty
Summary:  uWSGI - Plugin for PTY support
Group:    System Environment/Daemons
Requires: python, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-pty
This package contains the pty plugin for uWSGI

%package -n %{name}-plugin-python
Summary:  uWSGI - Plugin for Python support
Group:    System Environment/Daemons
Requires: python, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-python
This package contains the python plugin for uWSGI

%package -n %{name}-plugin-python3
Summary:  uWSGI - Plugin for Python 3 support
Group:    System Environment/Daemons
Requires: python%{python3_pkgversion}, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-python3
This package contains the Python 3 plugin for uWSGI

%package -n %{name}-plugin-rack
Summary:  uWSGI - Ruby rack plugin
Group:    System Environment/Daemons
Requires: rubygem-rack, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-rack
This package contains the rack plugin for uWSGI

%package -n %{name}-plugin-rbthreads
Summary:  uWSGI - Ruby native threads support plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, ruby

%description -n %{name}-plugin-rbthreads
This package contains the rbthreads plugin for uWSGI

%if %{with java}
%package -n %{name}-plugin-ring
Summary:  uWSGI - Clojure/Ring request handler support plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, %{name}-plugin-jvm = %{version}-%{release}, clojure

%description -n %{name}-plugin-ring
This package contains the ring plugin for uWSGI
%endif

%package -n %{name}-plugin-rpc
Summary:  uWSGI - Plugin for RPC support
Group:    System Environment/Daemons
Requires: rrdtool, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-rpc
This package contains the RPC plugin for uWSGI

%package -n %{name}-plugin-rrdtool
Summary:  uWSGI - Plugin for RRDTool support
Group:    System Environment/Daemons
Requires: rrdtool, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-rrdtool
This package contains the RRD Tool plugin for uWSGI

%package -n %{name}-plugin-ruby
Summary:  uWSGI - Plugin for Ruby support
Group:    System Environment/Daemons
Requires: ruby, %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-ruby
This package contains the ruby19 plugin for uWSGI

%package -n %{name}-plugin-spooler
Summary:  uWSGI - Plugin for Remote Spooling support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-spooler
This package contains the spooler plugin for uWSGI

%package -n %{name}-plugin-sqlite3
Summary:  uWSGI - SQLite3 plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, sqlite

%description -n %{name}-plugin-sqlite3
This package contains the sqlite3 plugin for uWSGI

%package -n %{name}-plugin-ssi
Summary:  uWSGI - Server Side Includes plugin
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-ssi
This package contains the ssi plugin for uWSGI

%package -n %{name}-plugin-tornado
Summary:  uWSGI - Plugin for Tornado support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, python-tornado

%description -n %{name}-plugin-tornado
This package contains the tornado plugin for uWSGI

%package -n %{name}-plugin-tornado3
Summary:  uWSGI - Plugin for Tornado/Python3 support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, python3-tornado

%description -n %{name}-plugin-tornado3
This package contains the tornado (python v3) plugin for uWSGI

%package -n %{name}-plugin-ugreen
Summary:  uWSGI - Plugin for uGreen support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-ugreen
This package contains the uGreen plugin for uWSGI

%if %{with v8}
%package -n %{name}-plugin-v8
Summary:  uWSGI - Plugin for v8 support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-v8
This package contains the v8 plugin for uWSGI
%endif

%package -n %{name}-plugin-webdav
Summary:  uWSGI - Plugin for WebDAV support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libattr

%description -n %{name}-plugin-webdav
This package contains the webdav plugin for uWSGI

%package -n %{name}-plugin-xattr
Summary:  uWSGI - Plugin for Extra Attributes support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libattr

%description -n %{name}-plugin-xattr
This package contains the xattr plugin for uWSGI

%package -n %{name}-plugin-xslt
Summary:  uWSGI - Plugin for XSLT transformation support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}, libxslt

%description -n %{name}-plugin-xslt
This package contains the xslt plugin for uWSGI

%package -n %{name}-plugin-zergpool
Summary:  uWSGI - Plugin for zergpool support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-plugin-zergpool
This package contains the zergpool plugin for uWSGI

# Routers

%package -n %{name}-router-access
Summary:   uWSGI - Plugin for router_access router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-access
This package contains the router_access plugin for uWSGI

%package -n %{name}-router-basicauth
Summary:   uWSGI - Plugin for Basic Auth router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-basicauth
This package contains the basicauth plugin for uWSGI

%package -n %{name}-router-cache
Summary:   uWSGI - Plugin for Cache router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-cache
This package contains the cache router plugin for uWSGI

%package -n %{name}-router-expires
Summary:   uWSGI - Plugin for Expires router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-expires
This package contains the expires router plugin for uWSGI

%package -n %{name}-router-fast
Summary:   uWSGI - Plugin for FastRouter support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-plugin-fastrouter <= 2.0.6
Provides:  %{name}-plugin-fastrouter = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-fast
This package contains the fastrouter (proxy) plugin for uWSGI

%package -n %{name}-router-forkpty
Summary:   uWSGI - Plugin for ForkPTY router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-router-forkpty
This package contains the ForkPTY router plugin for uWSGI

%package -n %{name}-router-hash
Summary:   uWSGI - Plugin for Hash router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-hash
This package contains the hash router plugin for uWSGI

%package -n %{name}-router-http
Summary:   uWSGI - Plugin for HTTP router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-http
This package contains the http router plugin for uWSGI

%package -n %{name}-router-memcached
Summary:   uWSGI - Plugin for Memcached router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-memcached
This package contains the memcached router plugin for uWSGI

%package -n %{name}-router-metrics
Summary:   uWSGI - Plugin for Metrics router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-router-metrics
This package contains the metrics router plugin for uWSGI

%package -n %{name}-router-radius
Summary:   uWSGI - Plugin for Radius router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-router-radius
This package contains the metrics router plugin for uWSGI

%package -n %{name}-router-raw
Summary:   uWSGI - Plugin for Raw Router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-plugin-rawrouter <= 2.0.6
Provides:  %{name}-plugin-rawrouter = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-raw
This package contains the Raw router plugin for uWSGI

%package -n %{name}-router-redirect
Summary:   uWSGI - Plugin for Redirect router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-redirect
This package contains the redirect router plugin for uWSGI

%package -n %{name}-router-redis
Summary:   uWSGI - Plugin for Redis router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-redis
This package contains the redis router plugin for uWSGI

%package -n %{name}-router-rewrite
Summary:   uWSGI - Plugin for Rewrite router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-rewrite
This package contains the rewrite router plugin for uWSGI

%package -n %{name}-router-spnego
Summary:   uWSGI - Plugin for SPNEgo router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-router-spnego
This package contains the spnego router plugin for uWSGI

%package -n %{name}-router-ssl
Summary:   uWSGI - Plugin for SSL router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Obsoletes: %{name}-plugin-sslrouter <= 2.0.6
Provides:  %{name}-plugin-sslrouter = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-ssl
This package contains the SSL router plugin for uWSGI

%package -n %{name}-router-static
Summary:   uWSGI - Plugin for Static router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-static
This package contains the Static router plugin for uWSGI

%package -n %{name}-router-tuntap
Summary:   uWSGI - Plugin for TUN/TAP router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}

%description -n %{name}-router-tuntap
This package contains the tuntap router plugin for uWSGI

%package -n %{name}-router-uwsgi
Summary:   uWSGI - Plugin for uWSGI router support
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-uwsgi
This package contains the uwsgi router plugin for uWSGI

%package -n %{name}-router-xmldir
Summary:   uWSGI - Plugin for XMLDir router rupport
Group:     System Environment/Daemons
Requires:  %{name}-plugin-common = %{version}-%{release}
Provides:  %{name}-routers = %{version}-%{release}

%description -n %{name}-router-xmldir
This package contains the xmldir router plugin for uWSGI

# The rest

%package -n mod_proxy_%{name}
Summary:  uWSGI - Apache2 proxy module
Group:    System Environment/Daemons
Requires: %{name} = %{version}-%{release}, httpd

%description -n mod_proxy_%{name}
Fully Apache API compliant proxy module


%prep
%setup -q
cp -p %{SOURCE1} buildconf/
%if %{with systemd}
cp -p %{SOURCE2} %{name}.service
%else
cp -p %{SOURCE6} %{name}.init
%endif
cp -p %{SOURCE3} %{name}.ini
cp -p %{SOURCE4} uwsgi-docs.tar.gz
cp -p %{SOURCE5} README.Fedora
echo "plugin_dir = %{_libdir}/%{name}" >> buildconf/$(basename %{SOURCE1})
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%if 0%{?fedora} >= 22
%patch5 -p1
%endif
%if %{with v8} && 0%{?fedora} >= 25
%patch6 -p1
%endif

#disable plug-ins
%if %{without mongodblibs}
sed -in "s/mongodblog, //" buildconf/fedora.ini
sed -in "s/stats_pusher_mongodb, //" buildconf/fedora.ini
%endif
%if %{without v8}
sed -in "s/v8, //" buildconf/fedora.ini
%endif
%if %{without gridfs}
sed -in "s/gridfs, //" buildconf/fedora.ini
%endif
%if %{without mono}
sed -in "s/mono, //" buildconf/fedora.ini
%endif


%build
CFLAGS="%{optflags} -Wno-error -Wno-unused-but-set-variable" python uwsgiconfig.py --build fedora.ini
%if %{with python3}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python3} uwsgiconfig.py --plugin plugins/python fedora python3
%if %{with tornado3}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python3} uwsgiconfig.py --plugin plugins/tornado fedora tornado3
%endif
%endif
%if %{with mongodblibs}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/mongodblog fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable -std=gnu++11 -Wno-error" python uwsgiconfig.py --plugin plugins/stats_pusher_mongodb fedora
%endif
%if %{with mono}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/mono fedora
%endif
%if %{with v8}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/v8 fedora
%endif
%if %{with go}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/gccgo fedora
%endif
%if %{with ruby19}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/fiber fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/rbthreads fedora
%endif
%if %{with systemd}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/systemd_logger fedora
%endif
%if %{with tuntap}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/tuntap fedora
%endif
%if %{with perl}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/psgi fedora
%if 0%{?fedora} >= 15
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/coroae fedora
%endif
%endif
%if %{with zeromq}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/logzmq fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/mongrel2 fedora
%endif
%if %{with greenlet}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/greenlet fedora
%endif
%if %{with glusterfs}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/glusterfs fedora
%endif
%if %{with gridfs}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/gridfs fedora
%endif
%if %{with java}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/jvm fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/jwsgi fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --plugin plugins/ring fedora
%endif
%{_httpd_apxs} -Wc,-Wall -Wl -c apache2/mod_proxy_uwsgi.c

%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}.d
mkdir -p %{buildroot}%{_usrsrc}/%{name}/%{version}
%if %{with systemd}
mkdir -p %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_initddir}
%endif
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_includedir}/%{name}
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_javadir}
mkdir -p %{buildroot}/run/%{name}
mkdir -p %{buildroot}%{_httpd_moddir}
%if %{with mono}
mkdir -p %{buildroot}%{_monogacdir}
%endif
mkdir docs
tar -C docs/ --strip-components=1 -xvzf uwsgi-docs.tar.gz
tar -C %{buildroot}%{_usrsrc}/%{name}/%{version} --strip-components=1 -xvzf %{SOURCE0}
cp %{SOURCE1} %{buildroot}%{_usrsrc}/%{name}/%{version}/buildconf/
cp docs/Changelog-%{majornumber}.%{minornumber}.%{releasenumber}.rst CHANGELOG
rm -f docs/.gitignore
echo "%{commit}, i.e. this:" >> README.Fedora
echo "https://github.com/unbit/%{docrepo}/tree/%{commit}" >> README.Fedora
%{__install} -p -m 0755 %{name} %{buildroot}%{_sbindir}
%{__install} -p -m 0644 *.h %{buildroot}%{_includedir}/%{name}
%{__install} -p -m 0755 *_plugin.so %{buildroot}%{_libdir}/%{name}
%{__install} -D -p -m 0644 uwsgidecorators.py %{buildroot}%{python_sitelib}/uwsgidecorators.py
%if %{manual_py_compile} == 1
%py_byte_compile %{__python} %{buildroot}%{python_sitelib}/
%endif
%if %{with python3}
%{__install} -D -p -m 0644 uwsgidecorators.py %{buildroot}%{python3_sitelib}/uwsgidecorators.py
%if %{manual_py_compile} == 1
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}/
%endif
%endif
%if %{with java}
%{__install} -p -m 0644 plugins/jvm/%{name}.jar %{buildroot}%{_javadir}
%endif
%if %{with mono}
gacutil -i plugins/mono/uwsgi.dll -f -package %{name} -root %{buildroot}/usr/lib
%endif
%{__install} -p -m 0644 %{name}.ini %{buildroot}%{_sysconfdir}/%{name}.ini
%if %{with systemd}
%{__install} -p -m 0644 %{name}.service %{buildroot}%{_unitdir}/%{name}.service
%else
%{__install} -p -m 0755 %{name}.init %{buildroot}%{_initddir}/%{name}
%endif
%{__install} -p -m 0755 apache2/.libs/mod_proxy_%{name}.so %{buildroot}%{_httpd_moddir}/mod_proxy_%{name}.so


%pre
getent group uwsgi >/dev/null || groupadd -r uwsgi
getent passwd uwsgi >/dev/null || \
    useradd -r -g uwsgi -d /run/uwsgi -s /sbin/nologin \
    -c "uWSGI daemon user" uwsgi
exit 0

%post
%if %{with systemd}
echo "Executing systemd post-install tasks"
%if 0%{?systemd_post:1}
    %systemd_post uwsgi.service
%else
    if [ $1 -eq 1 ] ; then
        # Initial installation
        /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    fi
%endif
%else
echo "Executing System V post-install tasks"
/sbin/chkconfig --add %{name}
%endif

%preun
%if %{with systemd}
echo "Executing systemd pre-uninstall tasks"
%if 0%{?systemd_preun:1}
    %systemd_preun uwsgi.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable uwsgi.service > /dev/null 2>&1 || :
        /bin/systemctl stop uwsgi.service > /dev/null 2>&1 || :
    fi
%endif
%else
echo "Executing System V pre-uninstall tasks"
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
%endif

%postun
%if %{with systemd}
echo "Executing systemd post-uninstall tasks"
%if 0%{?systemd_postun:1}
    %systemd_postun uwsgi.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ $1 -ge 1 ] ; then
        # Package upgrade, not uninstall
        /bin/systemctl try-restart uwsgi.service >/dev/null 2>&1 || :
    fi
%endif
%else
echo "Executing System V post-uninstall tasks"
if [ "$1" -ge "1" ] ; then
    /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi
%endif


%files
%{_sbindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.ini
%if %{with systemd}
%config %{_unitdir}/%{name}.service
%else
%{_initddir}/%{name}
%endif
%dir %{_sysconfdir}/%{name}.d
%dir /run/%{name}
%doc README README.Fedora CHANGELOG
%{!?_licensedir:%global license %%doc}
%license LICENSE

%files -n %{name}-devel
%{_includedir}/%{name}
%{_usrsrc}/%{name}

%files -n python-uwsgidecorators
%defattr(-,root,root,-)
%{python_sitelib}/*

%if %{with python3}
%files -n python3-uwsgidecorators
%defattr(-,root,root,-)
%{python3_sitelib}/*
%endif

%files -n %{name}-docs
%doc docs

%files -n %{name}-plugin-common
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/http_plugin.so
%{_libdir}/%{name}/cgi_plugin.so

# Stats pushers

%files -n %{name}-stats-pusher-file
%{_libdir}/%{name}/stats_pusher_file_plugin.so

%if %{with mongodblibs}
%files -n %{name}-stats-pusher-mongodb
%{_libdir}/%{name}/stats_pusher_mongodb_plugin.so
%endif

%files -n %{name}-stats-pusher-socket
%{_libdir}/%{name}/stats_pusher_socket_plugin.so

%files -n %{name}-stats-pusher-statsd
%{_libdir}/%{name}/stats_pusher_statsd_plugin.so

%files -n %{name}-stats-pusher-zabbix
%{_libdir}/%{name}/zabbix_plugin.so

# Alarms

%files -n %{name}-alarm-curl
%{_libdir}/%{name}/alarm_curl_plugin.so

%files -n %{name}-alarm-xmpp
%{_libdir}/%{name}/alarm_xmpp_plugin.so

# Transformations

%files -n %{name}-transformation-chunked
%{_libdir}/%{name}/transformation_chunked_plugin.so

%files -n %{name}-transformation-gzip
%{_libdir}/%{name}/transformation_gzip_plugin.so

%files -n %{name}-transformation-offload
%{_libdir}/%{name}/transformation_offload_plugin.so

%files -n %{name}-transformation-template
%{_libdir}/%{name}/transformation_template_plugin.so

%files -n %{name}-transformation-tofile
%{_libdir}/%{name}/transformation_tofile_plugin.so

%files -n %{name}-transformation-toupper
%{_libdir}/%{name}/transformation_toupper_plugin.so

# Loggers

%files -n %{name}-log-encoder-msgpack
%{_libdir}/%{name}/msgpack_plugin.so

%files -n %{name}-logger-crypto
%{_libdir}/%{name}/logcrypto_plugin.so

%files -n %{name}-logger-file
%{_libdir}/%{name}/logfile_plugin.so

%files -n %{name}-logger-graylog2
%{_libdir}/%{name}/graylog2_plugin.so

%if %{with mongodblibs}
%files -n %{name}-logger-mongodb
%{_libdir}/%{name}/mongodblog_plugin.so
%endif

%files -n %{name}-logger-pipe
%{_libdir}/%{name}/logpipe_plugin.so

%files -n %{name}-logger-redis
%{_libdir}/%{name}/redislog_plugin.so

%files -n %{name}-logger-rsyslog
%{_libdir}/%{name}/rsyslog_plugin.so

%files -n %{name}-logger-socket
%{_libdir}/%{name}/logsocket_plugin.so

%files -n %{name}-logger-syslog
%{_libdir}/%{name}/syslog_plugin.so

%if %{with systemd}
%files -n %{name}-logger-systemd
%{_libdir}/%{name}/systemd_logger_plugin.so
%endif

%if %{with zeromq}
%files -n %{name}-logger-zeromq
%{_libdir}/%{name}/logzmq_plugin.so
%endif

# Plugins

%files -n %{name}-plugin-airbrake
%{_libdir}/%{name}/airbrake_plugin.so

%files -n %{name}-plugin-cache
%{_libdir}/%{name}/cache_plugin.so

%files -n %{name}-plugin-carbon
%{_libdir}/%{name}/carbon_plugin.so

%if %{with perl}
%files -n %{name}-plugin-psgi
%{_libdir}/%{name}/psgi_plugin.so

%if 0%{?fedora} >= 15
%files -n %{name}-plugin-coroae
%{_libdir}/%{name}/coroae_plugin.so
%endif
%endif

%files -n %{name}-plugin-cheaper-busyness
%{_libdir}/%{name}/cheaper_busyness_plugin.so

%files -n %{name}-plugin-cplusplus
%{_libdir}/%{name}/cplusplus_plugin.so

%files -n %{name}-plugin-curl-cron
%{_libdir}/%{name}/curl_cron_plugin.so

%files -n %{name}-plugin-dumbloop
%{_libdir}/%{name}/dumbloop_plugin.so

%files -n %{name}-plugin-dummy
%{_libdir}/%{name}/dummy_plugin.so

%if %{with ruby19}
%files -n %{name}-plugin-fiber
%{_libdir}/%{name}/fiber_plugin.so
%endif

%if %{with go}
%files -n %{name}-plugin-gccgo
%{_libdir}/%{name}/gccgo_plugin.so
%endif

%files -n %{name}-plugin-geoip
%{_libdir}/%{name}/geoip_plugin.so

%files -n %{name}-plugin-gevent
%{_libdir}/%{name}/gevent_plugin.so

%if %{with glusterfs}
%files -n %{name}-plugin-glusterfs
%{_libdir}/%{name}/glusterfs_plugin.so
%endif

%if %{with greenlet}
%files -n %{name}-plugin-greenlet
%{_libdir}/%{name}/greenlet_plugin.so
%endif

%if %{with gridfs}
%files -n %{name}-plugin-gridfs
%{_libdir}/%{name}/gridfs_plugin.so
%endif

%if %{with java}
%files -n %{name}-plugin-jvm
%{_libdir}/%{name}/jvm_plugin.so
%{_javadir}/uwsgi.jar

%files -n %{name}-plugin-jwsgi
%{_libdir}/%{name}/jwsgi_plugin.so
%endif

%files -n %{name}-plugin-ldap
%{_libdir}/%{name}/ldap_plugin.so

%files -n %{name}-plugin-lua
%{_libdir}/%{name}/lua_plugin.so

%if %{with zeromq}
%files -n %{name}-plugin-mongrel2
%{_libdir}/%{name}/mongrel2_plugin.so
%endif

%if %{with mono}
%files -n %{name}-plugin-mono
%{_libdir}/%{name}/mono_plugin.so
%{_monodir}/%{name}/
%{_monogacdir}/%{name}/
%endif

%files -n %{name}-plugin-nagios
%{_libdir}/%{name}/nagios_plugin.so

%files -n %{name}-plugin-notfound
%{_libdir}/%{name}/notfound_plugin.so

%files -n %{name}-plugin-pam
%{_libdir}/%{name}/pam_plugin.so

%files -n %{name}-plugin-php
%{_libdir}/%{name}/php_plugin.so

%files -n %{name}-plugin-pty
%{_libdir}/%{name}/pty_plugin.so

%files -n %{name}-plugin-python
%{_libdir}/%{name}/python_plugin.so

%if %{with python3}
%files -n %{name}-plugin-python3
%{_libdir}/%{name}/python3_plugin.so
%endif

%files -n %{name}-plugin-rack
%{_libdir}/%{name}/rack_plugin.so

%if %{with ruby19}
%files -n %{name}-plugin-rbthreads
%{_libdir}/%{name}/rbthreads_plugin.so
%endif

%if %{with java}
%files -n %{name}-plugin-ring
%{_libdir}/%{name}/ring_plugin.so
%endif

%files -n %{name}-plugin-rrdtool
%{_libdir}/%{name}/rrdtool_plugin.so

%files -n %{name}-plugin-rpc
%{_libdir}/%{name}/rpc_plugin.so

%files -n %{name}-plugin-ruby
%{_libdir}/%{name}/ruby19_plugin.so

%files -n %{name}-plugin-spooler
%{_libdir}/%{name}/spooler_plugin.so

%files -n %{name}-plugin-sqlite3
%{_libdir}/%{name}/sqlite3_plugin.so

%files -n %{name}-plugin-ssi
%{_libdir}/%{name}/ssi_plugin.so

%files -n %{name}-plugin-tornado
%{_libdir}/%{name}/tornado_plugin.so

%if %{with tornado3}
%files -n %{name}-plugin-tornado3
%{_libdir}/%{name}/tornado3_plugin.so
%endif

%files -n %{name}-plugin-ugreen
%{_libdir}/%{name}/ugreen_plugin.so

%if %{with v8}
%files -n %{name}-plugin-v8
%{_libdir}/%{name}/v8_plugin.so
%endif

%files -n %{name}-plugin-webdav
%{_libdir}/%{name}/webdav_plugin.so

%files -n %{name}-plugin-xattr
%{_libdir}/%{name}/xattr_plugin.so

%files -n %{name}-plugin-xslt
%{_libdir}/%{name}/xslt_plugin.so

%files -n %{name}-plugin-zergpool
%{_libdir}/%{name}/zergpool_plugin.so

# Routers

%files -n %{name}-router-access
%{_libdir}/%{name}/router_access_plugin.so

%files -n %{name}-router-basicauth
%{_libdir}/%{name}/router_basicauth_plugin.so

%files -n %{name}-router-cache
%{_libdir}/%{name}/router_cache_plugin.so

%files -n %{name}-router-expires
%{_libdir}/%{name}/router_expires_plugin.so

%files -n %{name}-router-fast
%{_libdir}/%{name}/fastrouter_plugin.so

%files -n %{name}-router-forkpty
%{_libdir}/%{name}/forkptyrouter_plugin.so

%files -n %{name}-router-hash
%{_libdir}/%{name}/router_hash_plugin.so

%files -n %{name}-router-http
%{_libdir}/%{name}/router_http_plugin.so

%files -n %{name}-router-memcached
%{_libdir}/%{name}/router_memcached_plugin.so

%files -n %{name}-router-metrics
%{_libdir}/%{name}/router_metrics_plugin.so

%files -n %{name}-router-radius
%{_libdir}/%{name}/router_radius_plugin.so

%files -n %{name}-router-raw
%{_libdir}/%{name}/rawrouter_plugin.so

%files -n %{name}-router-redirect
%{_libdir}/%{name}/router_redirect_plugin.so

%files -n %{name}-router-redis
%{_libdir}/%{name}/router_redis_plugin.so

%files -n %{name}-router-rewrite
%{_libdir}/%{name}/router_rewrite_plugin.so

%files -n %{name}-router-spnego
%{_libdir}/%{name}/router_spnego_plugin.so

%files -n %{name}-router-ssl
%{_libdir}/%{name}/sslrouter_plugin.so

%files -n %{name}-router-static
%{_libdir}/%{name}/router_static_plugin.so

%if %{with tuntap}
%files -n %{name}-router-tuntap
%{_libdir}/%{name}/tuntap_plugin.so
%endif

%files -n %{name}-router-uwsgi
%{_libdir}/%{name}/router_uwsgi_plugin.so

%files -n %{name}-router-xmldir
%{_libdir}/%{name}/router_xmldir_plugin.so

# The rest

%files -n mod_proxy_%{name}
%{_httpd_moddir}/mod_proxy_%{name}.so


%changelog
* Fri Jan 13 2017 Jorge A Gallegos <kad@blegh.net> - 2.0.14-6
- Adding the cheaper_busyness plugin (Jorge Gallegos)
- Got tired of this giant string (Jorge Gallegos)

* Fri Jan 13 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.0.14-5
- F-26: rebuild for ruby24

* Thu Dec 22 2016 Miro Hrončok <mhroncok@redhat.com> - 2.0.14-4
- Rebuild for Python 3.6

* Tue Dec 20 2016 Carl George <carl.george@rackspace.com> - 2.0.14-3
- Enable plugin-psgi on EL7

* Wed Nov 30 2016 Carl George <carl.george@rackspace.com> - 2.0.14-2
- uwsgi is not yet OpenSSL 1.1 compatible, build against compat-openssl10 on F26+ (Carl George)
- php plugin requires krb5 headers to build (Carl George)

* Wed Oct 05 2016 Jorge A Gallegos <kad@blegh.net> - 2.0.14-1
- Updated to latest upstream stable (Jorge Gallegos)
- Make subpackage interdependencies versioned for bz #1368488 (Jorge Gallegos)
- chmod uwsgi sock file for bz #1338038 (Jorge Gallegos)
- greenlet and gevent depend on python bz #1325524 (Jorge Gallegos)
- config(noreplace) for uwsgi.ini bz #1339558 (Jorge Gallegos)

* Mon Aug 01 2016 Carl George <carl.george@rackspace.com> - 2.0.13.1-2
- Build against v8-314 on F25+ rhbz#1339293
- Own /usr/src/uwsgi rhbz#1351796

* Thu Jul 28 2016 Jorge A Gallegos <kad@blegh.net> - 2.0.13.1-1
- Bumped to latest stable

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.12-9
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue May 17 2016 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.12-8
- Perl 5.24 rebuild

* Tue Apr 12 2016 Peter Robinson <pbrobinson@fedoraproject.org> 2.0.12-7
- Mongodb doesn't depend on v8 anymore so is now supported on all LE arches

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.12-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 29 2016 Jonathan Wakely <jwakely@redhat.com> - 2.0.12-5
- Rebuilt for Boost 1.60

* Wed Jan 13 2016 Vít Ondruch <vondruch@redhat.com> - 2.0.12-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.3

* Thu Jan 07 2016 Jorge A Gallegos <kad@blegh.net> - 2.0.12-3
- Really fixing stats_pusher_mongodb (Jorge Gallegos)

* Sat Jan 02 2016 Jorge A Gallegos <kad@blegh.net> - 2.0.12-2
- Trying again with GCC

* Thu Dec 31 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.12-1
- Adding the build profile to -devel subpackage (Jorge Gallegos)
- Fixing stats-pusher-mongo for gnu++11 (Jorge Gallegos)
- Using _mono macros instead of hardcoded paths (Jorge Gallegos)
- Modifying an old changelog entry for rpmlint (Jorge Gallegos)
- Making -devel not pull unnecessary deps (Jorge Gallegos)
- Adjusting rpath patch for new release (Jorge Gallegos)
- Updating to latest stable version 2.0.12 (Jorge Gallegos)

* Fri Dec 11 2015 Ville Skyttä <ville.skytta@iki.fi> - 2.0.11.2-7
- Don't build tornado3 for EL7 (no python3-tornado available yet)
- Fix EL7 ppc64le build

* Sun Dec  6 2015 Peter Robinson <pbrobinson@fedoraproject.org> 2.0.11.2-6
- Fixing glusterfs for non x86_64 on el7

* Thu Nov 19 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.11.2-5
- Fixing manual brp-compiling in el6

* Wed Nov 18 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.11.2-4
- Fixing glusterfs for ppc64

* Tue Nov 17 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.11.2-3
- Fixing bz #1247395 - python3 plugin for epel7
- Fixing bz #1261942 - daemonize properly in SystemV
- Fixing bz #1258388 - package uwsgidecorators
- Fixing bz #1242155 - glusterfs plugin for epel7
- Fixing bz #1240236 - add source to -devel subpackage

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.11.2-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Fri Nov 06 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.11.2-1
- With latest stable

* Fri Aug 28 2015 Jonathan Wakely <jwakely@redhat.com> - 2.0.11.1-4
- Rebuilt for Boost 1.59

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.11.1-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 2.0.11.1-2
- rebuild for Boost 1.58

* Tue Jul 21 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.11.1-1
- New emergency security release

* Thu Jul 02 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.11-1
- Adding the dummy and notfound plugins (Jorge Gallegos)
- License is license (Jorge Gallegos)
- Mark config files as config (Jorge Gallegos)
- Adding sources for new version (Jorge Gallegos)
- uwsgi_fix_glibc_compatibility merged upstream (Jorge Gallegos)

* Tue Jun 23 2015 Thomas Spura <tomspur@fedoraproject.org> - 2.0.9-11
- rebuilt for new zeromq 4.1.2

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.9-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Jun 06 2015 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.9-9
- Perl 5.22 rebuild

* Mon May 18 2015 Peter Robinson <pbrobinson@fedoraproject.org> 2.0.9-8
- Rebuild (mono4)

* Thu Apr 23 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.9-7
- Disabled java related plugins (jvm, jwsgi, ring) in el6 ppc64

* Tue Apr 21 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.9-6
- Reworked the conditionals in the spec file
- Updated documentation
- Disabled PSGI for epel, builds fine but requirement is missing
- Reenabled systemd for epel7, dunno how I missed that one

* Fri Apr 17 2015 Dan Horák <dan[at]danny.cz> - 2.0.9-5
- conditionalize various subpackages depending on architectures (patch by Jakub Cajka) - #1211616

* Tue Apr 14 2015 Vít Ondruch <vondruch@redhat.com> - 2.0.9-4
- Fix glibc and MongoDB compatibility.

* Fri Mar 13 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.9-3
- Adding missing dist tag, have no clue at what point this got dropped :(

* Thu Mar 12 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.9-2
- Making it arch specific due to missing dependencies in PPC (as per
  https://fedoraproject.org/wiki/Packaging:Guidelines#BuildRequires)

* Wed Mar 11 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.9-1
- EPEL 6 and EPEL 7 compatible
- Plugins not compatible with epel 6 are systemd, go, python3 based, ruby19 based, gridfs and tuntap
- Plugins not compatible with epel 7 are python3 based, zeromq, greenlet, coroae, glusterfs and gridfs

* Fri Feb 27 2015 Jorge A Gallegos <kad@blegh.net> - 2.0.9-0
- New version

* Fri Jan 16 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.0.7-3
- Rebuild for https://fedoraproject.org/wiki/Changes/Ruby_2.2

* Thu Sep 18 2014 Jorge A Gallegos <kad@blegh.net> - 2.0.7-2
- -plugin-http doesn't exist, is in -plugin-common (Jorge Gallegos)

* Mon Sep 08 2014 Jorge A Gallegos <kad@blegh.net> - 2.0.7-1
- I am just done now, and there's a new version out already. Go figure.

* Sun Sep 07 2014 Jorge A Gallegos <kad@blegh.net> - 2.0.6-1
- Adding -stats-pusher-zabbix (Jorge Gallegos)
- Adding -plugin-xslt (Jorge Gallegos)
- Adding -plugin-webdav (Jorge Gallegos)
- Adding -plugin-v8 (Jorge Gallegos)
- Adding -router-tuntap (Jorge Gallegos)
- Adding http transformation plugins (Jorge Gallegos)
- Adding -plugin-tornado and -plugin-tornado3 (Jorge Gallegos)
- Adding all -stats-pusher-* plugins (Jorge Gallegos)
- Adding -plugin-ssi (Jorge Gallegos)
- Adding -plugin-ldap (Jorge Gallegos)
- Adding -plugin-sqlite3 (Jorge Gallegos)
- Adding -plugin-spooler (Jorge Gallegos)
- Adding -plugin-jwsgi (Jorge Gallegos)
- Adding -plugin-ring (Jorge Gallegos)
- Adding -plugin-rbthreads (Jorge Gallegos)
- Adding -plugin-pty (Jorge Gallegos)
- Adding -log-encoder-msgpack (Jorge Gallegos)
- Adding -plugin-mono (Jorge Gallegos)
- Adding -plugin-mongrel2 (Jorge Gallegos)
- Adding -plugin-gridfs (Jorge Gallegos)
- Adding -logger-graylog2 (Jorge Gallegos)
- Adding -plugin-glusterfs (Jorge Gallegos)
- Adding -plugin-gevent (Jorge Gallegos)
- Adding -plugin-geoip (Jorge Gallegos)
- Adding -plugin-gccgo (Jorge Gallegos)
- Adding -plugin-fiber (Jorge Gallegos)
- Adding -plugin-dumbloop (Jorge Gallegos)
- Adding -plugin-curl-cron (Jorge Gallegos)
- Adding -plugin-cplusplus (Jorge Gallegos)
- Adding -plugin-coroae (Jorge Gallegos)
- Adding -alarm-xmpp (Jorge Gallegos)
- Adding -alarm-curl (Jorge Gallegos)
- Packaging -plugin-airbrake (Jorge Gallegos)
- Broke up -routers into its individual -router-* (Jorge Gallegos)
- Renaming -plugin-sslrouter to -router-ssl (Jorge Gallegos)
- Renaming -plugin-rawrouter to -router-raw (Jorge Gallegos)
- Splitting off the documentation to its subpackage (Jorge Gallegos)
- Splitting off some non-essential embedded plugins: (Jorge Gallegos)
- Splitting off -logger-syslog (Jorge Gallegos)
- Splitting off -logger-rsyslog (Jorge Gallegos)
- Splitting off -logger-redis (Jorge Gallegos)
- Splitting off -logger-mongodb (Jorge Gallegos)
- Splitting off -logger-socket (Jorge Gallegos)
- Splitting off -logger-file (Jorge Gallegos)
- Splitting off -logger-pipe (Jorge Gallegos)
- Splitting off -logger-crypto instead (Jorge Gallegos)
- Break out the major/minor/release numbers properly (Jorge Gallegos)
- Reorganized spec, alphabetical and type (Jorge Gallegos)
- Splitting -router-fastrouter out of -common (Jorge Gallegos)
- Splitting out the README, I will be putting more stuff in here (Jorge Gallegos)
- Adding -logger-systemd plugin (Jorge Gallegos)
- Adding -logger-zeromq plugin (Jorge Gallegos)
- Adding new sources for newest stable (Jorge Gallegos)

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.19-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 1.9.19-5
- rebuild for https://fedoraproject.org/wiki/Changes/Php56

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.19-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 28 2014 Kalev Lember <kalevlember@gmail.com> - 1.9.19-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Tue Apr 29 2014 Vít Ondruch <vondruch@redhat.com> - 1.9.19-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.1

* Tue Nov 12 2013 Jorge A Gallegos <kad@blegh.net> - 1.9.19-1
- Updating to latest stable, uploading new sources (Jorge Gallegos)
- Forgot to delete the jvm arm patch file (Jorge Gallegos)

* Sun Oct 20 2013 Jorge A Gallegos <kad@blegh.net> - 1.9.18.2-1
- The changelog entry must match major + minor (Jorge Gallegos)
- Adding more ignore entries (Jorge Gallegos)
- The jvm arm patch has been merged upstream (Jorge Gallegos)
- Updated license to 'GPLv2 with exceptions' (Jorge Gallegos)
- Ugh messed up the doc sha (Jorge Gallegos)
- Adding new sources, bumping up spec to 1.9.18.2 (Jorge Gallegos)

* Sat Oct 19 2013 Jorge A Gallegos <kad@fedoraproject.org> - 1.9.18.2-0
- Breaking up full version in 3 parts (Jorge Gallegos)
- Update to latest stable 1.9.18.2 (Jorge Gallegos)
- Forgot to disable debug mode (Jorge Gallegos)

* Wed Oct 09 2013 Jorge A Gallegos <kad@blegh.net> - 1.9.17-2
- Uploaded new sources per spec rework (Jorge Gallegos)
- Adding more router plugins (Jorge Gallegos)
- Adding mod_proxy_uwsgi apache module (Jorge Gallegos)
- Complying with the guidelines for source urls (Jorge Gallegos)
- The settings in the service file were right before (Jorge Gallegos)
- Enabling stats log socket, and capabilities (Jorge Gallegos)

* Thu Oct 03 2013 Jorge A Gallegos <kad@blegh.net> - 1.9.17-1
- Copying the version changelog to top-level doc
- Compile with POSIX capabilities
- Embed the loggers into the binary itself, no need for an extra package
- Patching jvm plugin to support arm

* Wed Oct 02 2013 Jorge A Gallegos <kad@fedoraproject.org> - 1.9.17-0
- Rebuilt for version 1.9.17
- Pulling in new documentation from https://github.com/unbit/uwsgi-docs

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.8-1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Apr 23 2013 Jorge A Gallegos <kad@blegh.net> - 1.9.8-0
- Rebuilt with latest stable version from upstream

* Thu Apr 11 2013 Jorge A Gallegos <kad@blegh.net> - 1.9.5-0
- Rebuilt with latest stable version from upstream
- Added Erlang, PAM and JVM plugins
- Added router-related plugins
- Added logger plugins

* Tue Apr 02 2013 Vít Ondruch <vondruch@redhat.com> - 1.2.6-10
- Rebuild for https://fedoraproject.org/wiki/Features/Ruby_2.0.0

* Sat Mar 23 2013 Remi Collet <rcollet@redhat.com> - 1.2.6-9
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Feb 14 2013 Jorge A Gallegos <kad@blegh.net> - 1.2.6-7
- Tyrant mode shouldn't be used here, tyrant mode is root-only

* Thu Dec 27 2012 Jorge A Gallegos <kad@blegh.net> - 1.2.6-6
- Systemd now supports an exit status directive, fixing bugz 873382

* Fri Nov  9 2012 Remi Collet <rcollet@redhat.com> - 1.2.6-5
- rebuild against new php embedded library soname (5.4)

* Thu Oct 18 2012 Remi Collet <remi@fedoraproject.org> - 1.2.6-4
- rebuild for new PHP 5.4.8

* Wed Sep 19 2012 Jorge A Gallegos <kad@blegh.net> - 1.2.6-3
- Dropped requirement on PHP for the PHP plugin

* Sat Sep 15 2012 Jorge A Gallegos <kad@blegh.net> - 1.2.6-2
- Rebuilt with new systemd macros

* Sun Sep 09 2012 Jorge A Gallegos <kad@blegh.net> - 1.2.6-1
- Updated to latest stable from upstream

* Sat Aug 04 2012 David Malcolm <dmalcolm@redhat.com> - 1.2.4-4
- rebuild for https://fedoraproject.org/wiki/Features/Python_3.3

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jul 08 2012 Jorge A Gallegos <kad@blegh.net> - 1.2.4-1
- Updated to latest stable from upstream

* Tue Jun 26 2012 Jorge A Gallegos <kad@blegh.net> - 1.2.3-1
- Updated to latest stable upstream
- Building the pytho3 plugin is a bit trickier now, but still possible
- Added PHP plugin
- Added Carbon plugin
- Added RRDTool plugin
- Added rsyslog plugin
- Added syslog plugin

* Sun Feb 19 2012 Jorge A Gallegos <kad@blegh.net> - 1.0.4-1
- Addressing issues from package review feedback
- s/python-devel/python2-devel
- Make the libdir subdir owned by -plugins-common
- Upgraded to latest stable upstream version

* Mon Feb 06 2012 Jorge A Gallegos <kad@blegh.net> - 1.0.2.1-2
- Fixing 'unstripped-binary-or-object'

* Thu Jan 19 2012 Jorge A Gallegos <kad@blegh.net> - 1.0.2.1-1
- New upstream version

* Thu Dec 08 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.3-1
- New upstream version

* Sun Oct 09 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.2-2
- Don't download the wiki page at build time

* Sun Oct 09 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.2-1
- Updated to latest stable version
- Correctly linking plugin_dir
- Patches 1 and 2 were addressed upstream

* Sun Aug 21 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.8.3-3
- Got rid of BuildRoot
- Got rid of defattr()

* Sun Aug 14 2011 Jorge Gallegos <kad@blegh.net> - 0.9.8.3-2
- Added uwsgi_fix_rpath.patch
- Backported json_loads patch to work with jansson 1.x and 2.x
- Deleted clean steps since they are not needed in fedora

* Sun Jul 24 2011 Jorge Gallegos <kad@blegh.net> - 0.9.8.3-1
- rebuilt
- Upgraded to latest stable version 0.9.8.3
- Split packages

* Sun Jul 17 2011 Jorge Gallegos <kad@blegh.net> - 0.9.6.8-2
- Heavily modified based on Oskari's work

* Mon Feb 28 2011 Oskari Saarenmaa <os@taisia.fi> - 0.9.6.8-1
- Initial.
