#! /usr/bin/env sh

rm -f /usr/local/apache2/conf/tls-enabled
if [ -z "$IKN_TLS_DISABLED" ]; then
    touch /usr/local/apache2/conf/tls-enabled
fi
exec httpd-foreground
