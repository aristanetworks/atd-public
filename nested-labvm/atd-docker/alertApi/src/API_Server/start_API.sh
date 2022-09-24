#!/bin/sh
echo 'Start Web Hook API server and Memcache'

if pgrep -x "" >/dev/null
then
    echo "memcached is running"
else
    memcached -d -u memcache
    echo "Started memcached"
fi
cd /opt
if pgrep -x "uwsgi" >/dev/null
then
    echo "uwsgi is running will restart it"
    pkill -3 "uwsgi"
fi
echo "starting uwsgi with ini file uwsgi_conf"
uwsgi --ini uwsgi_conf.ini
