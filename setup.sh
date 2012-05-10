#!/bin/bash

apt-get install nginx squid varnish apache2 udp2log udp-filter git-core realpath

test -d /var/log/udp2log || mkdir -vp /var/log/udp2log
test -d /var/www/mediawiki || mkdir -vp /var/www/mediawiki
test -d /var/www/mediawiki/core || (cd /var/www/mediawiki && git clone https://gerrit.wikimedia.org/r/p/mediawiki/core.git)

mkdir -p /root/original_configs

function create_link {
    file=$(realpath -s $1)
    target=$(realpath -s $2)
    
    current_target=$(readlink -e ${target})
    
    if [ "${current_target}" == "${file}" ]; then
        return;
    fi
    
    test -f "${target}" && mv "${target}" "/root/original_configs/$(basename ${target})";
    ln -vs "${file}" "${target}";
}

create_link ./nginx.conf /etc/nginx.conf
create_link ./nginx.ssl_proxy /etc/nginx/sites-available/ssl_proxy
create_link ./nginx.ssl_proxy /etc/nginx/sites-enabled/ssl_proxy

create_link ./apache2.conf /etc/apache2/apache2.conf
create_link ./apache.default.vhost /etc/apache2/sites-available/000-default
create_link ./apache.default.vhost /etc/apache2/sites-enabled/000-default
create_link ./apache.mediawiki.vhost /etc/apache2/sites-available/001-mediawiki
create_link ./apache.mediawiki.vhost /etc/apache2/sites-enabled/001-mediawiki

create_link ./mediawiki.LocalSettings.php /var/www/mediawiki/core/LocalSettings.php

create_link ./squid.conf /etc/squid/squid.conf

create_link ./udp2log /etc/udp2log

create_link ./varnish.default.vcl /etc/varnish/default.vcl
create_link ./varnishncsa.default /etc/default/varnishncsa
create_link ./varnishncsa.init /etc/init.d/varnishncsa

