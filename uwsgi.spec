# Documentation sources:
%global commit 32a8f7304d0e705d36dd9644707552939c67f547
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global docrepo uwsgi-docs

%{!?_httpd_apxs: %{expand: %%global _httpd_apxs %%{_sbindir}/apxs}}
%{!?_httpd_moddir: %{expand: %%global _httpd_moddir %%{_libdir}/httpd/modules}}

# This is primarily built for fedora, make it easy right now
%if 0%{?fedora}
%bcond_without systemd
%bcond_without go
%bcond_without python3
# Fedora doesn't have two versions of python3
%bcond_with python3_other
%bcond_without ruby19
%bcond_without tuntap
%bcond_without zeromq
%bcond_without python2_greenlet
%bcond_without perl
%bcond_without glusterfs
%bcond_without java
# Fedora httpd includes mod_proxy_uwsgi
# https://bugzilla.redhat.com/show_bug.cgi?id=1574335
%bcond_with mod_proxy_uwsgi
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
%bcond_with python3_other
# el6 ships with ruby 1.8 but fiberloop/rbthreads needs 1.9
%bcond_with ruby19
# el6 doesn't have perl-PSGI
# el6 does have perl-Coro
%bcond_with perl
# el6 httpd does not include mod_proxy_uwsgi
%bcond_without mod_proxy_uwsgi
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
# el7 has another version of python3
%bcond_without python3_other
# el7 doesn't have zeromq
%bcond_with zeromq
# el7 does have python-greenlet, but only on x86_64
%ifarch x86_64
%bcond_without python2_greenlet
%else
%bcond_with python2_greenlet
%endif
# el7 does have perl-PSGI
# el7 does have perl-Coro
%bcond_without perl
# el7 httpd does not include mod_proxy_uwsgi
%bcond_without mod_proxy_uwsgi
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

# Disable router_access in fedora >= 28 because tcp_wrappers deprecation
%if 0%{?fedora} >= 28
%bcond_with tcp_wrappers
%else
%bcond_without tcp_wrappers
%endif

Name:           uwsgi
Version:        2.0.17.1
Release:        8%{?dist}
Summary:        Fast, self-healing, application container server
License:        GPLv2 with exceptions
URL:            https://github.com/unbit/uwsgi
Source0:        http://projects.unbit.it/downloads/uwsgi-%{version}.tar.gz
Source1:        fedora.ini
Source2:        uwsgi.service
Source3:        emperor.ini
Source4:        https://github.com/unbit/%{docrepo}/archive/%{commit}/%{docrepo}-%{shortcommit}.tar.gz
Source5:        README.Fedora
Source6:        uwsgi.init
Source7:        uwsgi.tmpfiles
Patch0:         uwsgi_trick_chroot_rpmbuild.patch
Patch1:         uwsgi_fix_rpath.patch
Patch2:         uwsgi_ruby20_compatibility.patch
Patch3:         uwsgi_fix_lua.patch
# https://github.com/unbit/uwsgi/issues/882
Patch5:         uwsgi_fix_mongodb.patch
Patch6:         uwsgi_v8-314_compatibility.patch
Patch7:         uwsgi_fix_mono.patch
# https://github.com/unbit/uwsgi/pull/1772
Patch9:         uwsgi-2.0.16-glfs.patch
BuildRequires:  curl,  python2-devel, libxml2-devel, libuuid-devel, jansson-devel
BuildRequires:  libyaml-devel, ruby-devel
%if %{with tcp_wrappers}
BuildRequires:  tcp_wrappers-devel
%endif
%if %{with python3}
BuildRequires:  python%{python3_pkgversion}-devel
%endif
%if %{with python3_other}
BuildRequires:  python%{python3_other_pkgversion}-devel
%endif
%if %{with python2_greenlet}
BuildRequires:  python-greenlet-devel
%endif
%if %{with python3}
BuildRequires:  python%{python3_pkgversion}-greenlet-devel
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
%ifarch %arm
# FIXME: explicitly specify java package not to use
# java-1.8.0-openjdk-aarch32, which provides client/libjvm.so
# but not server/libjvm.so, which uwsgi requires
BuildRequires:  java-1.8.0-openjdk-headless
BuildRequires:  java-1.8.0-openjdk-devel
%endif
BuildRequires:  java-devel, sqlite-devel, libcap-devel
BuildRequires:  httpd-devel, libcurl-devel
BuildRequires:  gloox-devel, libstdc++-devel
BuildRequires:  GeoIP-devel, libevent-devel, zlib-devel
BuildRequires:  openldap-devel, boost-devel
BuildRequires:  libattr-devel, libxslt-devel
%if %{with perl}
BuildRequires:  perl-devel, perl-ExtUtils-Embed, perl-Coro
%endif
%if %{with zeromq}
BuildRequires:  zeromq-devel
%endif
%if %{with go}
BuildRequires:  gcc-go
%endif
%if %{with systemd}
BuildRequires:  systemd-devel, systemd-units
%endif
%if %{with mono}
BuildRequires:  mono-devel, mono-web, glib2-devel
%endif
%if %{with v8}
%if 0%{?fedora} >= 25
BuildRequires:  v8-314-devel
%else
BuildRequires:  v8-devel
%endif
%endif
%if %{with mongodblibs}
%if 0%{?fedora} >= 30
BuildRequires:  mongo-cxx-driver-legacy-devel
%else
BuildRequires:  libmongodb-devel
%endif
%endif

%if 0%{?fedora} >= 28
BuildRequires:  libargon2-devel
Obsoletes:      uwsgi-router-access <= 2.0.16
%endif

Obsoletes:      uwsgi-loggers <= 1.9.8-1
Obsoletes:      uwsgi-routers <= 2.0.6
Obsoletes:      uwsgi-plugin-erlang <= 1.9.20-1
Obsoletes:      uwsgi-plugin-admin <= 2.0.6

Requires(pre):    shadow-utils
%if %{with systemd}
%{?systemd_requires}
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

%filter_requires_in %{_usrsrc}
%filter_provides_in %{_usrsrc}
%filter_provides_in %{_libdir}/uwsgi/.*\.so$
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

%package -n uwsgi-devel
Summary:    uWSGI - Development header files and libraries
Requires:   uwsgi = %{version}-%{release}

%description -n uwsgi-devel
This package contains the development header files and libraries
for uWSGI extensions

%if 0%{?fedora} < 30
%package -n python2-uwsgidecorators
Summary:        Python 2 decorators providing access to the uwsgi API
Requires:       uwsgi = %{version}-%{release}
Requires:       uwsgi-plugin-python2 = %{version}-%{release}
Obsoletes:      python-uwsgidecorators < 2.0.16-4

%description -n python2-uwsgidecorators
The uwsgidecorators Python 2 module provides higher-level access to the uWSGI API.
%endif

%if %{with python3}
%package -n python%{python3_pkgversion}-uwsgidecorators
Summary:        Python %{python3_version} decorators providing access to the uwsgi API
Requires:       uwsgi = %{version}-%{release}
Requires:       uwsgi-plugin-python%{python3_pkgversion} = %{version}-%{release}
%if 0%{?rhel} == 7
Obsoletes:      python3-uwsgidecorators < 2.0.16-4
%endif

%description -n python%{python3_pkgversion}-uwsgidecorators
The uwsgidecorators Python %{python3_version} module provides higher-level access to the uWSGI API.
%endif

%if %{with python3_other}
%package -n python%{python3_other_pkgversion}-uwsgidecorators
Summary:        Python %{python3_other_version} decorators providing access to the uwsgi API
Requires:       uwsgi = %{version}-%{release}
Requires:       uwsgi-plugin-python%{python3_other_pkgversion} = %{version}-%{release}

%description -n python%{python3_other_pkgversion}-uwsgidecorators
The uwsgidecorators Python %{python3_other_version} module provides higher-level access to the uWSGI API.
%endif

%package -n uwsgi-docs
Summary:  uWSGI - Documentation
Requires: uwsgi

%description -n uwsgi-docs
This package contains the documentation files for uWSGI

%package -n uwsgi-plugin-common
Summary:  uWSGI - Common plugins for uWSGI
Requires: uwsgi = %{version}-%{release}

%description -n uwsgi-plugin-common
This package contains the most common plugins used with uWSGI. The
plugins included in this package are: cache, CGI, RPC, uGreen

# Stats pushers

%package -n uwsgi-stats-pusher-file
Summary:    uWSGI - File Stats Pusher for uWSGI
Requires:   uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-stats-pusher-file
This package contains the stats_pusher_file plugin for uWSGI

%if %{with mongodblibs}
%package -n uwsgi-stats-pusher-mongodb
Summary:    uWSGI - MongoDB Stats Pusher for uWSGI
Requires:   uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-stats-pusher-mongodb
This package contains the stats_pusher_mongodb plugin for uWSGI
%endif

%package -n uwsgi-stats-pusher-socket
Summary:    uWSGI - Socket Stats Pusher for uWSGI
Requires:   uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-stats-pusher-socket
This package contains the stats_pusher_socket plugin for uWSGI

%package -n uwsgi-stats-pusher-statsd
Summary:    uWSGI - StatsD Stats Pusher for uWSGI
Requires:   uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-stats-pusher-statsd
This package contains the stats_pusher_statsd plugin for uWSGI

%package -n uwsgi-stats-pusher-zabbix
Summary:    uWSGI - Zabbix Stats Pusher for uWSGI
Requires:   uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-stats-pusher-zabbix
This package contains the zabbix plugin for uWSGI

# Alarms

%package -n uwsgi-alarm-curl
Summary:  uWSGI - Curl alarm plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, libcurl

%description -n uwsgi-alarm-curl
This package contains the alarm_curl alarm plugin for uWSGI

%package -n uwsgi-alarm-xmpp
Summary:  uWSGI - Curl alarm plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, gloox

%description -n uwsgi-alarm-xmpp
This package contains the alarm_xmpp alarm plugin for uWSGI

# Transformations

%package -n uwsgi-transformation-chunked
Summary:  uWSGI - Chunked Transformation plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-router-uwsgi = %{version}-%{release}

%description -n uwsgi-transformation-chunked
This package contains the transformation_chunked plugin for uWSGI

%package -n uwsgi-transformation-gzip
Summary:  uWSGI - GZip Transformation plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-router-uwsgi = %{version}-%{release}

%description -n uwsgi-transformation-gzip
This package contains the transformation_gzip plugin for uWSGI

%package -n uwsgi-transformation-offload
Summary:  uWSGI - Off-Load Transformation plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-router-uwsgi = %{version}-%{release}

%description -n uwsgi-transformation-offload
This package contains the transformation_offload plugin for uWSGI

%package -n uwsgi-transformation-template
Summary:  uWSGI - Template Transformation plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-router-uwsgi = %{version}-%{release}

%description -n uwsgi-transformation-template
This package contains the transformation_template plugin for uWSGI

%package -n uwsgi-transformation-tofile
Summary:  uWSGI - ToFile Transformation plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-router-uwsgi = %{version}-%{release}

%description -n uwsgi-transformation-tofile
This package contains the transformation_tofile plugin for uWSGI

%package -n uwsgi-transformation-toupper
Summary:  uWSGI - ToUpper Transformation plugin
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-transformation-toupper
This package contains the transformation_toupper plugin for uWSGI

# Loggers

%package -n uwsgi-log-encoder-msgpack
Summary:  uWSGI - msgpack log encoder plugin
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-log-encoder-msgpack
This package contains the msgpack log encoder plugin for uWSGI

%package -n uwsgi-logger-crypto
Summary:  uWSGI - logcrypto logger plugin
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-logger-crypto
This package contains the logcrypto logger plugin for uWSGI

%package -n uwsgi-logger-file
Summary:   uWSGI - logfile logger plugin
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-loggers <= 1.9.8-1
Provides:  uwsgi-loggers = %{version}-%{release}

%description -n uwsgi-logger-file
This package contains the logfile logger plugin for uWSGI

%package -n uwsgi-logger-graylog2
Summary:   uWSGI - Graylog2 logger plugin
Requires:  uwsgi-plugin-common = %{version}-%{release}, zlib

%description -n uwsgi-logger-graylog2
This package contains the graylog2 logger plugin for uWSGI

%if %{with mongodblibs}
%package -n uwsgi-logger-mongodb
Summary:   uWSGI - mongodblog logger plugin
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-loggers <= 1.9.8-1
Provides:  uwsgi-loggers = %{version}-%{release}

%description -n uwsgi-logger-mongodb
This package contains the mongodblog logger plugin for uWSGI
%endif

%package -n uwsgi-logger-pipe
Summary:  uWSGI - logpipe logger plugin
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-logger-pipe
This package contains the logcrypto logger plugin for uWSGI

%package -n uwsgi-logger-redis
Summary:   uWSGI - redislog logger plugin
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-loggers <= 1.9.8-1
Provides:  uwsgi-loggers = %{version}-%{release}

%description -n uwsgi-logger-redis
This package contains the redislog logger plugin for uWSGI

%package -n uwsgi-logger-rsyslog
Summary:   uWSGI - rsyslog logger plugin
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-plugin-rsyslog <= 1.9.8-1
Provides:  uwsgi-plugin-rsyslog = %{version}-%{release}

%description -n uwsgi-logger-rsyslog
This package contains the rsyslog logger plugin for uWSGI

%package -n uwsgi-logger-socket
Summary:   uWSGI - logsocket logger plugin
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-loggers <= 1.9.8-1
Provides:  uwsgi-loggers = %{version}-%{release}

%description -n uwsgi-logger-socket
This package contains the logsocket logger plugin for uWSGI

%package -n uwsgi-logger-syslog
Summary:   uWSGI - syslog logger plugin
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-plugin-syslog <= 1.9.8-1
Provides:  uwsgi-plugin-syslog = %{version}-%{release}

%description -n uwsgi-logger-syslog
This package contains the syslog logger plugin for uWSGI

%if %{with systemd}
%package -n uwsgi-logger-systemd
Summary:  uWSGI - systemd journal logger plugin
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-logger-systemd
This package contains the systemd journal logger plugin for uWSGI
%endif

%if %{with zeromq}
%package -n uwsgi-logger-zeromq
Summary:  uWSGI - ZeroMQ logger plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, zeromq

%description -n uwsgi-logger-zeromq
This package contains the ZeroMQ logger plugin for uWSGI
%endif

# Plugins

%package -n uwsgi-plugin-airbrake
Summary:  uWSGI - Plugin for AirBrake support
Requires: uwsgi-plugin-common = %{version}-%{release}, libcurl

%description -n uwsgi-plugin-airbrake
This package contains the airbrake plugin for uWSGI

%package -n uwsgi-plugin-cache
Summary:  uWSGI - Plugin for cache support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-cache
This package contains the cache plugin for uWSGI

%package -n uwsgi-plugin-carbon
Summary:  uWSGI - Plugin for Carbon/Graphite support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-carbon
This package contains the Carbon plugin for uWSGI (to use in graphite)

%if %{with perl}
%package -n uwsgi-plugin-psgi
Summary:  uWSGI - Plugin for PSGI support
Requires: perl-PSGI, uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-psgi
This package contains the PSGI plugin for uWSGI

%package -n uwsgi-plugin-coroae
Summary:  uWSGI - Plugin for PERL Coro support
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-plugin-psgi = %{version}-%{release}, perl-Coro

%description -n uwsgi-plugin-coroae
This package contains the coroae plugin for uWSGI
%endif

%package -n uwsgi-plugin-cheaper-busyness
Summary:  uWSGI - Plugin for Cheaper Busyness algos
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-cheaper-busyness
This package contains the cheaper_busyness plugin for uWSGI

%package -n uwsgi-plugin-cplusplus
Summary:  uWSGI - Plugin for C++ support
Requires: uwsgi-plugin-common = %{version}-%{release}, libstdc++

%description -n uwsgi-plugin-cplusplus
This package contains the cplusplus plugin for uWSGI

%package -n uwsgi-plugin-curl-cron
Summary:  uWSGI - Plugin for CURL Cron support
Requires: uwsgi-plugin-common = %{version}-%{release}, libcurl

%description -n uwsgi-plugin-curl-cron
This package contains the curl_cron plugin for uWSGI

%package -n uwsgi-plugin-dumbloop
Summary:  uWSGI - Plugin for Dumb Loop support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-dumbloop
This package contains the dumbloop plugin for uWSGI

%package -n uwsgi-plugin-dummy
Summary:  uWSGI - Plugin for Dummy support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-dummy
This package contains the dummy plugin for uWSGI

%package -n uwsgi-plugin-fiber
Summary:  uWSGI - Plugin for Ruby Fiber support
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-plugin-rack = %{version}-%{release}

%description -n uwsgi-plugin-fiber
This package contains the fiber plugin for uWSGI

%package -n uwsgi-plugin-gccgo
Summary:  uWSGI - Plugin for GoLang support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-gccgo
This package contains the gccgo plugin for uWSGI

%package -n uwsgi-plugin-geoip
Summary:  uWSGI - Plugin for GeoIP support
Requires: uwsgi-plugin-common = %{version}-%{release}, GeoIP

%description -n uwsgi-plugin-geoip
This package contains the geoip plugin for uWSGI

%package -n uwsgi-plugin-python2-gevent
Summary:  uWSGI - Plugin for Python 2 GEvent support
Requires: uwsgi-plugin-python2 = %{version}-%{release}, libevent
Obsoletes: uwsgi-plugin-gevent < 2.0.16-4

%description -n uwsgi-plugin-python2-gevent
This package contains the Python 2 gevent plugin for uWSGI

%if %{with python3}
%package -n uwsgi-plugin-python%{python3_pkgversion}-gevent
Summary:  uWSGI - Plugin for Python %{python3_version} GEvent support
Requires: uwsgi-plugin-python%{python3_pkgversion} = %{version}-%{release}, libevent

%description -n uwsgi-plugin-python%{python3_pkgversion}-gevent
This package contains the Python %{python3_version} gevent plugin for uWSGI
%endif

%if %{with python3_other}
%package -n uwsgi-plugin-python%{python3_other_pkgversion}-gevent
Summary:  uWSGI - Plugin for Python %{python3_other_version} GEvent support
Requires: uwsgi-plugin-python%{python3_other_pkgversion} = %{version}-%{release}, libevent

%description -n uwsgi-plugin-python%{python3_other_pkgversion}-gevent
This package contains the Python %{python3_other_version} gevent plugin for uWSGI
%endif

%if %{with glusterfs}
%package -n uwsgi-plugin-glusterfs
Summary:  uWSGI - Plugin for GlusterFS support
Requires: uwsgi-plugin-common = %{version}-%{release}, glusterfs-api

%description -n uwsgi-plugin-glusterfs
This package contains the glusterfs plugin for uWSGI
%endif

%if %{with python2_greenlet}
%package -n uwsgi-plugin-python2-greenlet
Summary:  uWSGI - Plugin for Python 2 Greenlet support
Requires: python-greenlet, uwsgi-plugin-python2 = %{version}-%{release}
Obsoletes: uwsgi-plugin-greenlet < 2.0.16-4

%description -n uwsgi-plugin-python2-greenlet
This package contains the Python 2 greenlet plugin for uWSGI
%endif

%if %{with python3}
%package -n uwsgi-plugin-python%{python3_pkgversion}-greenlet
Summary:  uWSGI - Plugin for Python %{python3_version} Greenlet support
Requires: python%{python3_pkgversion}-greenlet, uwsgi-plugin-python%{python3_pkgversion} = %{version}-%{release}

%description -n uwsgi-plugin-python%{python3_pkgversion}-greenlet
This package contains the Python %{python3_version} greenlet plugin for uWSGI
%endif

%if %{with gridfs}
%package -n uwsgi-plugin-gridfs
Summary:  uWSGI - Plugin for GridFS support
Requires: uwsgi-plugin-common = %{version}-%{release}, libmongodb

%description -n uwsgi-plugin-gridfs
This package contains the gridfs plugin for uWSGI
%endif

%if %{with java}
%package -n uwsgi-plugin-jvm
Summary:  uWSGI - Plugin for JVM support
Requires: uwsgi-plugin-common = %{version}-%{release}, java-headless, jpackage-utils

%description -n uwsgi-plugin-jvm
This package contains the JVM plugin for uWSGI

%package -n uwsgi-plugin-jwsgi
Summary:  uWSGI - Plugin for JWSGI support
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-plugin-jvm = %{version}-%{release}

%description -n uwsgi-plugin-jwsgi
This package contains the jwsgi plugin for uWSGI
%endif

%package -n uwsgi-plugin-ldap
Summary:  uWSGI - Plugin for LDAP support
Requires: uwsgi-plugin-common = %{version}-%{release}, openldap

%description -n uwsgi-plugin-ldap
This package contains the ldap plugin for uWSGI

%package -n uwsgi-plugin-lua
Summary:  uWSGI - Plugin for LUA support
Requires: lua, uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-lua
This package contains the lua plugin for uWSGI

%if %{with zeromq}
%package -n uwsgi-plugin-mongrel2
Summary:  uWSGI - Plugin for Mongrel2 support
Requires: uwsgi-plugin-common = %{version}-%{release}, zeromq

%description -n uwsgi-plugin-mongrel2
This package contains the mongrel2 plugin for uWSGI
%endif

%if %{with mono}
%package -n uwsgi-plugin-mono
Summary:  uWSGI - Plugin for Mono / .NET support
Requires: uwsgi-plugin-common = %{version}-%{release}, mono-web

%description -n uwsgi-plugin-mono
This package contains the mono plugin for uWSGI
%endif

%package -n uwsgi-plugin-nagios
Summary:  uWSGI - Plugin for Nagios support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-nagios
This package contains the nagios plugin for uWSGI

%package -n uwsgi-plugin-notfound
Summary:  uWSGI - Plugin for notfound support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-notfound
This package contains the notfound plugin for uWSGI

%package -n uwsgi-plugin-pam
Summary:  uWSGI - Plugin for PAM support
Requires: uwsgi-plugin-common = %{version}-%{release}, pam

%description -n uwsgi-plugin-pam
This package contains the PAM plugin for uWSGI

%package -n uwsgi-plugin-php
Summary:  uWSGI - Plugin for PHP support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-php
This package contains the PHP plugin for uWSGI

%package -n uwsgi-plugin-pty
Summary:  uWSGI - Plugin for PTY support
Requires: python2, uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-pty
This package contains the pty plugin for uWSGI

%package -n uwsgi-plugin-python2
Summary:  uWSGI - Plugin for Python 2 support
Requires: python2, uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-plugin-python < 2.0.16-4

%description -n uwsgi-plugin-python2
This package contains the Python 2 plugin for uWSGI

%if %{with python3}
%package -n uwsgi-plugin-python%{python3_pkgversion}
Summary:  uWSGI - Plugin for Python %{python3_version} support
Requires: python%{python3_pkgversion}, uwsgi-plugin-common = %{version}-%{release}
%if 0%{?rhel} == 7
Obsoletes: uwsgi-plugin-python3 < 2.0.16-4
%endif

%description -n uwsgi-plugin-python%{python3_pkgversion}
This package contains the Python %{python3_version} plugin for uWSGI
%endif

%if %{with python3_other}
%package -n uwsgi-plugin-python%{python3_other_pkgversion}
Summary:  uWSGI - Plugin for Python %{python3_other_version} support
Requires: python%{python3_other_pkgversion}, uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-python%{python3_other_pkgversion}
This package contains the Python %{python3_other_version} plugin for uWSGI
%endif

%package -n uwsgi-plugin-rack
Summary:  uWSGI - Ruby rack plugin
Requires: rubygem-rack, uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-rack
This package contains the rack plugin for uWSGI

%package -n uwsgi-plugin-rbthreads
Summary:  uWSGI - Ruby native threads support plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, ruby

%description -n uwsgi-plugin-rbthreads
This package contains the rbthreads plugin for uWSGI

%if %{with java}
%package -n uwsgi-plugin-ring
Summary:  uWSGI - Clojure/Ring request handler support plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, uwsgi-plugin-jvm = %{version}-%{release}, clojure

%description -n uwsgi-plugin-ring
This package contains the ring plugin for uWSGI
%endif

%package -n uwsgi-plugin-rpc
Summary:  uWSGI - Plugin for RPC support
Requires: rrdtool, uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-rpc
This package contains the RPC plugin for uWSGI

%package -n uwsgi-plugin-rrdtool
Summary:  uWSGI - Plugin for RRDTool support
Requires: rrdtool, uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-rrdtool
This package contains the RRD Tool plugin for uWSGI

%package -n uwsgi-plugin-ruby
Summary:  uWSGI - Plugin for Ruby support
Requires: ruby, uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-ruby
This package contains the ruby19 plugin for uWSGI

%package -n uwsgi-plugin-spooler
Summary:  uWSGI - Plugin for Remote Spooling support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-spooler
This package contains the spooler plugin for uWSGI

%package -n uwsgi-plugin-sqlite3
Summary:  uWSGI - SQLite3 plugin
Requires: uwsgi-plugin-common = %{version}-%{release}, sqlite

%description -n uwsgi-plugin-sqlite3
This package contains the sqlite3 plugin for uWSGI

%package -n uwsgi-plugin-ssi
Summary:  uWSGI - Server Side Includes plugin
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-ssi
This package contains the ssi plugin for uWSGI

%package -n uwsgi-plugin-python2-tornado
Summary:  uWSGI - Plugin for Tornado (Python 2) support
Requires: uwsgi-plugin-common = %{version}-%{release}, python-tornado
Obsoletes: uwsgi-plugin-tornado < 2.0.16-4

%description -n uwsgi-plugin-python2-tornado
This package contains the tornado (Python 2) plugin for uWSGI

%if %{with python3}
%package -n uwsgi-plugin-python%{python3_pkgversion}-tornado
Summary:  uWSGI - Plugin for Tornado (Python %{python3_version}) support
Requires: uwsgi-plugin-common = %{version}-%{release}, python%{python3_pkgversion}-tornado
%if 0%{?fedora} && 0%{?fedora} < 29
Obsoletes: uwsgi-plugin-tornado3 < 2.0.16-4
%endif

%description -n uwsgi-plugin-python%{python3_pkgversion}-tornado
This package contains the tornado (Python %{python3_version}) plugin for uWSGI
%endif

%package -n uwsgi-plugin-ugreen
Summary:  uWSGI - Plugin for uGreen support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-ugreen
This package contains the uGreen plugin for uWSGI

%if %{with v8}
%package -n uwsgi-plugin-v8
Summary:  uWSGI - Plugin for v8 support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-v8
This package contains the v8 plugin for uWSGI
%endif

%package -n uwsgi-plugin-webdav
Summary:  uWSGI - Plugin for WebDAV support
Requires: uwsgi-plugin-common = %{version}-%{release}, libattr

%description -n uwsgi-plugin-webdav
This package contains the webdav plugin for uWSGI

%package -n uwsgi-plugin-xattr
Summary:  uWSGI - Plugin for Extra Attributes support
Requires: uwsgi-plugin-common = %{version}-%{release}, libattr

%description -n uwsgi-plugin-xattr
This package contains the xattr plugin for uWSGI

%package -n uwsgi-plugin-xslt
Summary:  uWSGI - Plugin for XSLT transformation support
Requires: uwsgi-plugin-common = %{version}-%{release}, libxslt

%description -n uwsgi-plugin-xslt
This package contains the xslt plugin for uWSGI

%package -n uwsgi-plugin-zergpool
Summary:  uWSGI - Plugin for zergpool support
Requires: uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-plugin-zergpool
This package contains the zergpool plugin for uWSGI

# Routers

%if %{with tcp_wrappers}
%package -n uwsgi-router-access
Summary:   uWSGI - Plugin for router_access router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-access
This package contains the router_access plugin for uWSGI
%endif

%package -n uwsgi-router-basicauth
Summary:   uWSGI - Plugin for Basic Auth router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-basicauth
This package contains the basicauth plugin for uWSGI

%package -n uwsgi-router-cache
Summary:   uWSGI - Plugin for Cache router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-cache
This package contains the cache router plugin for uWSGI

%package -n uwsgi-router-expires
Summary:   uWSGI - Plugin for Expires router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-expires
This package contains the expires router plugin for uWSGI

%package -n uwsgi-router-fast
Summary:   uWSGI - Plugin for FastRouter support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-plugin-fastrouter <= 2.0.6
Provides:  uwsgi-plugin-fastrouter = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-fast
This package contains the fastrouter (proxy) plugin for uWSGI

%package -n uwsgi-router-forkpty
Summary:   uWSGI - Plugin for ForkPTY router support
Requires:  uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-router-forkpty
This package contains the ForkPTY router plugin for uWSGI

%package -n uwsgi-router-hash
Summary:   uWSGI - Plugin for Hash router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-hash
This package contains the hash router plugin for uWSGI

%package -n uwsgi-router-http
Summary:   uWSGI - Plugin for HTTP router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-http
This package contains the http router plugin for uWSGI

%package -n uwsgi-router-memcached
Summary:   uWSGI - Plugin for Memcached router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-memcached
This package contains the memcached router plugin for uWSGI

%package -n uwsgi-router-metrics
Summary:   uWSGI - Plugin for Metrics router support
Requires:  uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-router-metrics
This package contains the metrics router plugin for uWSGI

%package -n uwsgi-router-radius
Summary:   uWSGI - Plugin for Radius router support
Requires:  uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-router-radius
This package contains the metrics router plugin for uWSGI

%package -n uwsgi-router-raw
Summary:   uWSGI - Plugin for Raw Router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-plugin-rawrouter <= 2.0.6
Provides:  uwsgi-plugin-rawrouter = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-raw
This package contains the Raw router plugin for uWSGI

%package -n uwsgi-router-redirect
Summary:   uWSGI - Plugin for Redirect router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-redirect
This package contains the redirect router plugin for uWSGI

%package -n uwsgi-router-redis
Summary:   uWSGI - Plugin for Redis router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-redis
This package contains the redis router plugin for uWSGI

%package -n uwsgi-router-rewrite
Summary:   uWSGI - Plugin for Rewrite router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-rewrite
This package contains the rewrite router plugin for uWSGI

%package -n uwsgi-router-spnego
Summary:   uWSGI - Plugin for SPNEgo router support
Requires:  uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-router-spnego
This package contains the spnego router plugin for uWSGI

%package -n uwsgi-router-ssl
Summary:   uWSGI - Plugin for SSL router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Obsoletes: uwsgi-plugin-sslrouter <= 2.0.6
Provides:  uwsgi-plugin-sslrouter = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-ssl
This package contains the SSL router plugin for uWSGI

%package -n uwsgi-router-static
Summary:   uWSGI - Plugin for Static router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-static
This package contains the Static router plugin for uWSGI

%package -n uwsgi-router-tuntap
Summary:   uWSGI - Plugin for TUN/TAP router support
Requires:  uwsgi-plugin-common = %{version}-%{release}

%description -n uwsgi-router-tuntap
This package contains the tuntap router plugin for uWSGI

%package -n uwsgi-router-uwsgi
Summary:   uWSGI - Plugin for uWSGI router support
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-uwsgi
This package contains the uwsgi router plugin for uWSGI

%package -n uwsgi-router-xmldir
Summary:   uWSGI - Plugin for XMLDir router rupport
Requires:  uwsgi-plugin-common = %{version}-%{release}
Provides:  uwsgi-routers = %{version}-%{release}

%description -n uwsgi-router-xmldir
This package contains the xmldir router plugin for uWSGI

# The rest

%if %{with mod_proxy_uwsgi}
%package -n mod_proxy_uwsgi
Summary:  uWSGI - Apache2 proxy module
Requires: uwsgi = %{version}-%{release}, httpd

%description -n mod_proxy_uwsgi
Fully Apache API compliant proxy module
%endif


%prep
%setup -q
cp -p %{SOURCE1} buildconf/
echo "plugin_dir = %{_libdir}/uwsgi" >> buildconf/fedora.ini
cp -p %{SOURCE5} README.Fedora
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
%if %{with mono}
%patch7 -p1
%endif
%patch9 -p1 -b .glfs

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
CFLAGS="%{optflags} -Wno-error -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --build fedora.ini
%if %{with python3}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python3} uwsgiconfig.py --plugin plugins/python fedora python%{python3_pkgversion}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python3} uwsgiconfig.py --plugin plugins/gevent fedora python%{python3_pkgversion}_gevent
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python3} uwsgiconfig.py --plugin plugins/tornado fedora python%{python3_pkgversion}_tornado
%endif
%if %{with python3_other}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python3_other} uwsgiconfig.py --plugin plugins/python fedora python%{python3_other_pkgversion}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python3_other} uwsgiconfig.py --plugin plugins/gevent fedora python%{python3_other_pkgversion}_gevent
%endif
%if %{with mongodblibs}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/mongodblog fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable -std=gnu++11 -Wno-error" %{__python2} uwsgiconfig.py --plugin plugins/stats_pusher_mongodb fedora
%endif
%if %{with mono}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/mono fedora
%endif
%if %{with v8}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/v8 fedora
%endif
%if %{with go}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/gccgo fedora
%endif
%if %{with ruby19}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/fiber fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/rbthreads fedora
%endif
%if %{with systemd}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/systemd_logger fedora
%endif
%if %{with tuntap}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/tuntap fedora
%endif
%if %{with perl}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/psgi fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/coroae fedora
%endif
%if %{with zeromq}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/logzmq fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/mongrel2 fedora
%endif
%if %{with python2_greenlet}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/greenlet fedora
%endif
%if %{with python3}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python3} uwsgiconfig.py --plugin plugins/greenlet fedora python%{python3_pkgversion}_greenlet
%endif
%if %{with glusterfs}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/glusterfs fedora
%endif
%if %{with gridfs}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/gridfs fedora
%endif
%if %{with java}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/jvm fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/jwsgi fedora
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/ring fedora
%endif
%if %{with tcp_wrappers}
CFLAGS="%{optflags} -Wno-unused-but-set-variable" %{__python2} uwsgiconfig.py --plugin plugins/router_access fedora
%endif
%if %{with mod_proxy_uwsgi}
%{_httpd_apxs} -Wc,-Wall -Wl -c apache2/mod_proxy_uwsgi.c
%endif


%install
mkdir -p %{buildroot}%{_sysconfdir}/uwsgi.d
mkdir -p %{buildroot}%{_usrsrc}/uwsgi/%{version}
mkdir -p %{buildroot}%{_includedir}/uwsgi
mkdir -p %{buildroot}%{_libdir}/uwsgi
%if %{without systemd}
install -d -m 0775 %{buildroot}%{_localstatedir}/run/uwsgi
%endif
%if %{with mono}
mkdir -p %{buildroot}%{_monogacdir}
%endif
mkdir docs
tar -C docs/ --strip-components=1 -xvzf %{SOURCE4}
tar -C %{buildroot}%{_usrsrc}/uwsgi/%{version} --strip-components=1 -xvzf %{SOURCE0}
cp %{SOURCE1} %{buildroot}%{_usrsrc}/uwsgi/%{version}/buildconf/
cp docs/Changelog-%{version}.rst CHANGELOG
rm -f docs/.gitignore
echo "%{commit}, i.e. this:" >> README.Fedora
echo "https://github.com/unbit/%{docrepo}/tree/%{commit}" >> README.Fedora
install -D -p -m 0755 uwsgi %{buildroot}%{_sbindir}/uwsgi
install -p -m 0644 *.h %{buildroot}%{_includedir}/uwsgi
install -p -m 0755 *_plugin.so %{buildroot}%{_libdir}/uwsgi
%if 0%{?fedora} < 30
install -D -p -m 0644 uwsgidecorators.py %{buildroot}%{python2_sitelib}/uwsgidecorators.py
%endif
%if %{manual_py_compile} == 1
%py_byte_compile %{__python2} %{buildroot}%{python2_sitelib}/uwsgidecorators.py
%endif
%if %{with python3}
install -D -p -m 0644 uwsgidecorators.py %{buildroot}%{python3_sitelib}/uwsgidecorators.py
%if %{manual_py_compile} == 1
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}/uwsgidecorators.py
%endif
%endif
%if %{with python3_other}
install -D -p -m 0644 uwsgidecorators.py %{buildroot}%{python3_other_sitelib}/uwsgidecorators.py
%if %{manual_py_compile} == 1
%py_byte_compile %{__python3_other} %{buildroot}%{python3_other_sitelib}/uwsgidecorators.py
%endif
%endif
%if %{with java}
install -D -p -m 0644 plugins/jvm/uwsgi.jar %{buildroot}%{_javadir}/uwsgi.jar
%endif
%if %{with mono}
gacutil -i plugins/mono/uwsgi.dll -f -package uwsgi -root %{buildroot}/usr/lib
%endif
install -D -p -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/uwsgi.ini
%if %{with systemd}
install -D -p -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/uwsgi.service
install -D -p -m 0644 %{SOURCE7} %{buildroot}%{_tmpfilesdir}/uwsgi.conf
%else
install -D -p -m 0755 %{SOURCE6} %{buildroot}%{_initddir}/uwsgi
%endif
%if %{with mod_proxy_uwsgi}
install -D -p -m 0755 apache2/.libs/mod_proxy_uwsgi.so %{buildroot}%{_httpd_moddir}/mod_proxy_uwsgi.so
%endif


%pre
getent group uwsgi >/dev/null || groupadd -r uwsgi
getent passwd uwsgi >/dev/null || \
    useradd -r -g uwsgi -d %{!?with_systemd:%{_localstatedir}}/run/uwsgi -s /sbin/nologin \
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
/sbin/chkconfig --add uwsgi
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
    /sbin/service uwsgi stop >/dev/null 2>&1
    /sbin/chkconfig --del uwsgi
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
    /sbin/service uwsgi condrestart >/dev/null 2>&1 || :
fi
%endif


%files
%{_sbindir}/uwsgi
%config(noreplace) %{_sysconfdir}/uwsgi.ini
%if %{with systemd}
%{_unitdir}/uwsgi.service
%{_tmpfilesdir}/uwsgi.conf
%else
%{_initddir}/uwsgi
%endif
%dir %{_sysconfdir}/uwsgi.d
%if %{without systemd}
%attr(0775,uwsgi,uwsgi) %dir %{_localstatedir}/run/uwsgi
%endif
%doc README README.Fedora CHANGELOG
%license LICENSE

%files -n uwsgi-devel
%{_includedir}/uwsgi
%{_usrsrc}/uwsgi

%if 0%{?fedora} < 30
%files -n python2-uwsgidecorators
%{python2_sitelib}/uwsgidecorators.py*
%endif

%if %{with python3}
%files -n python%{python3_pkgversion}-uwsgidecorators
%{python3_sitelib}/uwsgidecorators.py
%{python3_sitelib}/__pycache__/uwsgidecorators.cpython-%{python3_version_nodots}*.py*
%endif

%if %{with python3_other}
%files -n python%{python3_other_pkgversion}-uwsgidecorators
%{python3_other_sitelib}/uwsgidecorators.py
%{python3_other_sitelib}/__pycache__/uwsgidecorators.cpython-%{python3_other_version_nodots}*.py*
%endif

%files -n uwsgi-docs
%doc docs

%files -n uwsgi-plugin-common
%dir %{_libdir}/uwsgi
%{_libdir}/uwsgi/http_plugin.so
%{_libdir}/uwsgi/cgi_plugin.so

# Stats pushers

%files -n uwsgi-stats-pusher-file
%{_libdir}/uwsgi/stats_pusher_file_plugin.so

%if %{with mongodblibs}
%files -n uwsgi-stats-pusher-mongodb
%{_libdir}/uwsgi/stats_pusher_mongodb_plugin.so
%endif

%files -n uwsgi-stats-pusher-socket
%{_libdir}/uwsgi/stats_pusher_socket_plugin.so

%files -n uwsgi-stats-pusher-statsd
%{_libdir}/uwsgi/stats_pusher_statsd_plugin.so

%files -n uwsgi-stats-pusher-zabbix
%{_libdir}/uwsgi/zabbix_plugin.so

# Alarms

%files -n uwsgi-alarm-curl
%{_libdir}/uwsgi/alarm_curl_plugin.so

%files -n uwsgi-alarm-xmpp
%{_libdir}/uwsgi/alarm_xmpp_plugin.so

# Transformations

%files -n uwsgi-transformation-chunked
%{_libdir}/uwsgi/transformation_chunked_plugin.so

%files -n uwsgi-transformation-gzip
%{_libdir}/uwsgi/transformation_gzip_plugin.so

%files -n uwsgi-transformation-offload
%{_libdir}/uwsgi/transformation_offload_plugin.so

%files -n uwsgi-transformation-template
%{_libdir}/uwsgi/transformation_template_plugin.so

%files -n uwsgi-transformation-tofile
%{_libdir}/uwsgi/transformation_tofile_plugin.so

%files -n uwsgi-transformation-toupper
%{_libdir}/uwsgi/transformation_toupper_plugin.so

# Loggers

%files -n uwsgi-log-encoder-msgpack
%{_libdir}/uwsgi/msgpack_plugin.so

%files -n uwsgi-logger-crypto
%{_libdir}/uwsgi/logcrypto_plugin.so

%files -n uwsgi-logger-file
%{_libdir}/uwsgi/logfile_plugin.so

%files -n uwsgi-logger-graylog2
%{_libdir}/uwsgi/graylog2_plugin.so

%if %{with mongodblibs}
%files -n uwsgi-logger-mongodb
%{_libdir}/uwsgi/mongodblog_plugin.so
%endif

%files -n uwsgi-logger-pipe
%{_libdir}/uwsgi/logpipe_plugin.so

%files -n uwsgi-logger-redis
%{_libdir}/uwsgi/redislog_plugin.so

%files -n uwsgi-logger-rsyslog
%{_libdir}/uwsgi/rsyslog_plugin.so

%files -n uwsgi-logger-socket
%{_libdir}/uwsgi/logsocket_plugin.so

%files -n uwsgi-logger-syslog
%{_libdir}/uwsgi/syslog_plugin.so

%if %{with systemd}
%files -n uwsgi-logger-systemd
%{_libdir}/uwsgi/systemd_logger_plugin.so
%endif

%if %{with zeromq}
%files -n uwsgi-logger-zeromq
%{_libdir}/uwsgi/logzmq_plugin.so
%endif

# Plugins

%files -n uwsgi-plugin-airbrake
%{_libdir}/uwsgi/airbrake_plugin.so

%files -n uwsgi-plugin-cache
%{_libdir}/uwsgi/cache_plugin.so

%files -n uwsgi-plugin-carbon
%{_libdir}/uwsgi/carbon_plugin.so

%if %{with perl}
%files -n uwsgi-plugin-psgi
%{_libdir}/uwsgi/psgi_plugin.so

%files -n uwsgi-plugin-coroae
%{_libdir}/uwsgi/coroae_plugin.so
%endif

%files -n uwsgi-plugin-cheaper-busyness
%{_libdir}/uwsgi/cheaper_busyness_plugin.so

%files -n uwsgi-plugin-cplusplus
%{_libdir}/uwsgi/cplusplus_plugin.so

%files -n uwsgi-plugin-curl-cron
%{_libdir}/uwsgi/curl_cron_plugin.so

%files -n uwsgi-plugin-dumbloop
%{_libdir}/uwsgi/dumbloop_plugin.so

%files -n uwsgi-plugin-dummy
%{_libdir}/uwsgi/dummy_plugin.so

%if %{with ruby19}
%files -n uwsgi-plugin-fiber
%{_libdir}/uwsgi/fiber_plugin.so
%endif

%if %{with go}
%files -n uwsgi-plugin-gccgo
%{_libdir}/uwsgi/gccgo_plugin.so
%endif

%files -n uwsgi-plugin-geoip
%{_libdir}/uwsgi/geoip_plugin.so

%files -n uwsgi-plugin-python2-gevent
%{_libdir}/uwsgi/gevent_plugin.so

%if %{with python3}
%files -n uwsgi-plugin-python%{python3_pkgversion}-gevent
%{_libdir}/uwsgi/python%{python3_pkgversion}_gevent_plugin.so
%endif

%if %{with python3_other}
%files -n uwsgi-plugin-python%{python3_other_pkgversion}-gevent
%{_libdir}/uwsgi/python%{python3_other_pkgversion}_gevent_plugin.so
%endif

%if %{with glusterfs}
%files -n uwsgi-plugin-glusterfs
%{_libdir}/uwsgi/glusterfs_plugin.so
%endif

%if %{with python2_greenlet}
%files -n uwsgi-plugin-python2-greenlet
%{_libdir}/uwsgi/greenlet_plugin.so
%endif

%if %{with python3}
%files -n uwsgi-plugin-python%{python3_pkgversion}-greenlet
%{_libdir}/uwsgi/python%{python3_pkgversion}_greenlet_plugin.so
%endif

%if %{with gridfs}
%files -n uwsgi-plugin-gridfs
%{_libdir}/uwsgi/gridfs_plugin.so
%endif

%if %{with java}
%files -n uwsgi-plugin-jvm
%{_libdir}/uwsgi/jvm_plugin.so
%{_javadir}/uwsgi.jar

%files -n uwsgi-plugin-jwsgi
%{_libdir}/uwsgi/jwsgi_plugin.so
%endif

%files -n uwsgi-plugin-ldap
%{_libdir}/uwsgi/ldap_plugin.so

%files -n uwsgi-plugin-lua
%{_libdir}/uwsgi/lua_plugin.so

%if %{with zeromq}
%files -n uwsgi-plugin-mongrel2
%{_libdir}/uwsgi/mongrel2_plugin.so
%endif

%if %{with mono}
%files -n uwsgi-plugin-mono
%{_libdir}/uwsgi/mono_plugin.so
%{_monodir}/uwsgi/
%{_monogacdir}/uwsgi/
%endif

%files -n uwsgi-plugin-nagios
%{_libdir}/uwsgi/nagios_plugin.so

%files -n uwsgi-plugin-notfound
%{_libdir}/uwsgi/notfound_plugin.so

%files -n uwsgi-plugin-pam
%{_libdir}/uwsgi/pam_plugin.so

%files -n uwsgi-plugin-php
%{_libdir}/uwsgi/php_plugin.so

%files -n uwsgi-plugin-pty
%{_libdir}/uwsgi/pty_plugin.so

%files -n uwsgi-plugin-python2
%{_libdir}/uwsgi/python_plugin.so

%if %{with python3}
%files -n uwsgi-plugin-python%{python3_pkgversion}
%{_libdir}/uwsgi/python%{python3_pkgversion}_plugin.so
%endif

%if %{with python3_other}
%files -n uwsgi-plugin-python%{python3_other_pkgversion}
%{_libdir}/uwsgi/python%{python3_other_pkgversion}_plugin.so
%endif

%files -n uwsgi-plugin-rack
%{_libdir}/uwsgi/rack_plugin.so

%if %{with ruby19}
%files -n uwsgi-plugin-rbthreads
%{_libdir}/uwsgi/rbthreads_plugin.so
%endif

%if %{with java}
%files -n uwsgi-plugin-ring
%{_libdir}/uwsgi/ring_plugin.so
%endif

%files -n uwsgi-plugin-rrdtool
%{_libdir}/uwsgi/rrdtool_plugin.so

%files -n uwsgi-plugin-rpc
%{_libdir}/uwsgi/rpc_plugin.so

%files -n uwsgi-plugin-ruby
%{_libdir}/uwsgi/ruby19_plugin.so

%files -n uwsgi-plugin-spooler
%{_libdir}/uwsgi/spooler_plugin.so

%files -n uwsgi-plugin-sqlite3
%{_libdir}/uwsgi/sqlite3_plugin.so

%files -n uwsgi-plugin-ssi
%{_libdir}/uwsgi/ssi_plugin.so

%files -n uwsgi-plugin-python2-tornado
%{_libdir}/uwsgi/tornado_plugin.so

%if %{with python3}
%files -n uwsgi-plugin-python%{python3_pkgversion}-tornado
%{_libdir}/uwsgi/python%{python3_pkgversion}_tornado_plugin.so
%endif

%files -n uwsgi-plugin-ugreen
%{_libdir}/uwsgi/ugreen_plugin.so

%if %{with v8}
%files -n uwsgi-plugin-v8
%{_libdir}/uwsgi/v8_plugin.so
%endif

%files -n uwsgi-plugin-webdav
%{_libdir}/uwsgi/webdav_plugin.so

%files -n uwsgi-plugin-xattr
%{_libdir}/uwsgi/xattr_plugin.so

%files -n uwsgi-plugin-xslt
%{_libdir}/uwsgi/xslt_plugin.so

%files -n uwsgi-plugin-zergpool
%{_libdir}/uwsgi/zergpool_plugin.so

# Routers

%if %{with tcp_wrappers}
%files -n uwsgi-router-access
%{_libdir}/uwsgi/router_access_plugin.so
%endif

%files -n uwsgi-router-basicauth
%{_libdir}/uwsgi/router_basicauth_plugin.so

%files -n uwsgi-router-cache
%{_libdir}/uwsgi/router_cache_plugin.so

%files -n uwsgi-router-expires
%{_libdir}/uwsgi/router_expires_plugin.so

%files -n uwsgi-router-fast
%{_libdir}/uwsgi/fastrouter_plugin.so

%files -n uwsgi-router-forkpty
%{_libdir}/uwsgi/forkptyrouter_plugin.so

%files -n uwsgi-router-hash
%{_libdir}/uwsgi/router_hash_plugin.so

%files -n uwsgi-router-http
%{_libdir}/uwsgi/router_http_plugin.so

%files -n uwsgi-router-memcached
%{_libdir}/uwsgi/router_memcached_plugin.so

%files -n uwsgi-router-metrics
%{_libdir}/uwsgi/router_metrics_plugin.so

%files -n uwsgi-router-radius
%{_libdir}/uwsgi/router_radius_plugin.so

%files -n uwsgi-router-raw
%{_libdir}/uwsgi/rawrouter_plugin.so

%files -n uwsgi-router-redirect
%{_libdir}/uwsgi/router_redirect_plugin.so

%files -n uwsgi-router-redis
%{_libdir}/uwsgi/router_redis_plugin.so

%files -n uwsgi-router-rewrite
%{_libdir}/uwsgi/router_rewrite_plugin.so

%files -n uwsgi-router-spnego
%{_libdir}/uwsgi/router_spnego_plugin.so

%files -n uwsgi-router-ssl
%{_libdir}/uwsgi/sslrouter_plugin.so

%files -n uwsgi-router-static
%{_libdir}/uwsgi/router_static_plugin.so

%if %{with tuntap}
%files -n uwsgi-router-tuntap
%{_libdir}/uwsgi/tuntap_plugin.so
%endif

%files -n uwsgi-router-uwsgi
%{_libdir}/uwsgi/router_uwsgi_plugin.so

%files -n uwsgi-router-xmldir
%{_libdir}/uwsgi/router_xmldir_plugin.so

# The rest

%if %{with mod_proxy_uwsgi}
%files -n mod_proxy_uwsgi
%{_httpd_moddir}/mod_proxy_uwsgi.so
%endif


%changelog
* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.17.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 21 2019 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.0.17.1-7
- F-30: rebuild against ruby26

* Mon Jan 14 2019 Björn Esser <besser82@fedoraproject.org> - 2.0.17.1-6
- Rebuilt for libcrypt.so.2 (#1666033)

* Fri Nov 02 2018 Carl George <carl@george.computer> - 2.0.17.1-5
- Don't build python2-uwsgidecorators on F30+
- BuildRequire mongo-cxx-driver-legacy-devel on F30+

* Wed Sep 12 2018 Carl George <carl@george.computer> - 2.0.17.1-4
- Drop mod_proxy_uwsgi subpackage on Fedora, as this module now provided by httpd rhbz#1574335

* Sat Jul 14 2018 Tadej Janež <tadej.j@nez.si> - 2.0.17.1-3
- Re-enable greenlet plugin on EL7:
  - Python 3 version is always built
  - Python 2 version is only built on x86_64

* Thu Jul 12 2018 Carl George <carl@george.computer> - 2.0.17.1-2
- Make python2-uwsgidecorators own the right files (rhbz#1600721)
- Be more explicit with uwsgidecorators files

* Mon Jul 09 2018 Carl George <carl@george.computer> - 2.0.17.1-1
- Latest upstream (rhbz#1549354)
- Enable uwsgi-plugin-coroae on EL7
- Use systemd tmpfiles to create /run/uwsgi with group write permissions (rhbz#1427303)
- Use /var/run/uwsgi when not using systemd
- Build with versioned python command
- Remove %%config from systemd unit file
- Disable greenlet plugin on EL7

* Tue Jul 03 2018 Petr Pisar <ppisar@redhat.com> - 2.0.16-7
- Perl 5.28 rebuild

* Fri Jun 29 2018 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.16-6
- Perl 5.28 rebuild

* Wed Jun 27 2018 Tadej Janež <tadej.j@nez.si> - 2.0.16-5
- Build Python 3 version(s) of gevent plugin on Fedora and EPEL7
- Build Python 3 version of greenlet plugin on Fedora and EPEL7
- Build Python 2 version of greenlet plugin on EPEL7
- Always build Python 3 version of tornado plugin when building with Python 3
  (drop python3_tornado build conditional)

* Tue Jun 26 2018 Tadej Janež <tadej.j@nez.si> - 2.0.16-4
- Modernize and generalize building of Python subpackages:
  - replace python with python2
  - use appropriate macros for when refering to Python 3
  - prefix Python-dependent plugins with the version of Python they are built
    with
- Also build Python 3 subpackages for the other Python 3 version in EPEL7

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 2.0.16-3
- Rebuilt for Python 3.7

* Tue Apr 03 2018 Till Maas <opensource@till.name> - 2.0.16-2
- Fix building in Rawhide (#1556525) (Jakub Jelen)
- Disable tcp_wrappers for Fedora 28 and newer (Jakub Jelen)

* Tue Feb 13 2018 Jorge A Gallegos <kad@blegh.net> - 2.0.16-1
- Conditionally disable router-access for tcp_wrappers deprecation (Jorge Gallegos)
- Updated to 2.0.16 which includes fix for CVE-2018-6758 (Jorge Gallegos)

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.15-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 2.0.15-8
- Rebuilt for switch to libxcrypt

* Tue Oct 03 2017 Remi Collet <remi@fedoraproject.org> - 2.0.15-7
- rebuild for https://fedoraproject.org/wiki/Changes/php72

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.15-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.15-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 21 2017 Kalev Lember <klember@redhat.com> - 2.0.15-4
- Rebuilt for Boost 1.64

* Fri Jul 07 2017 Igor Gnatenko <ignatenko@redhat.com> - 2.0.15-3
- Rebuild due to bug in RPM (RHBZ #1468476)

* Sun Jun 04 2017 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.15-2
- Perl 5.26 rebuild

* Thu May 18 2017 Jorge A Gallegos <kad@blegh.net> - 2.0.15-1
- Bumping release to 2.0.15 (Jorge Gallegos)
- Updating sources to 2.0.15 (Jorge Gallegos)

* Mon Mar 20 2017 Carl George <carl.george@rackspace.com> - 2.0.14-11
- Add patch7 to add glib-2.0 pkg-config flags to mono build
- Filter uwgi plugins from automatic provides rhbz#1352089

* Wed Feb 15 2017 Igor Gnatenko <ignatenko@redhat.com> - 2.0.14-10
- Rebuild for brp-python-bytecompile

* Wed Feb 08 2017 Carl George <carl.george@rackspace.com> - 2.0.14-9
- Rebuild for boost soname bump

* Sun Feb 05 2017 Kalev Lember <klember@redhat.com> - 2.0.14-8
- Rebuilt for libgo soname bump

* Sun Jan 15 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.0.14-7
- Workaround for build issue on arm(32): explicitly write 
  java-1.8.0-openjdk-headless as BR not to use java-1.8.0-openjdk-aarch32
  which does not provide server/libjvm.so

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
