#!/bin/bash

rm -rf /var/www/html/atd/labguides/
git clone https://github.com/aristanetworks/atd-public.git /tmp/atd
cd /tmp/atd/labguides
make html
sphinx-build -b latex source build
make latexpdf
mkdir /var/www/html/atd/labguides/
mv /tmp/atd/labguides/build/latex/ATD.pdf /var/www/html/atd/labguides/
mv /tmp/atd/labguides/build/html/* /var/www/html/atd/labguides/ && chown -R www-data:www-data /var/www/html/atd/labguides
rm -rf /tmp/atd
