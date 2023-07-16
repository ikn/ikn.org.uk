FROM httpd:2.4.57-alpine

COPY --chmod=755 startup.sh /
COPY httpd/ /usr/local/apache2/conf/
RUN rm -r /usr/local/apache2/htdocs/
COPY site/ /usr/local/apache2/htdocs/

CMD ["/startup.sh"]
