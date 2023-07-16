#! /usr/bin/env sh

if [ -z "$IKN_TLS_DISABLED" ]; then
    touch /usr/local/apache2/conf/tls-enabled
fi
exec httpd-foreground
