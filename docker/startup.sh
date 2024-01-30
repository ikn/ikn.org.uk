#! /usr/bin/env sh

rm -f /usr/local/apache2/conf/tls-enabled
if [ "$IKN_TLS_ENABLED" = true ]; then
    touch /usr/local/apache2/conf/tls-enabled
fi
exec httpd-foreground
