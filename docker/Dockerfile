FROM httpd:2.4.57-alpine

COPY httpd.conf /usr/local/apache2/conf/httpd.conf
RUN rm -r /usr/local/apache2/htdocs/
COPY site/ /usr/local/apache2/htdocs/
