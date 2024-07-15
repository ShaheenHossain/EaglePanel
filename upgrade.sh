#!/bin/bash
## Script to clear caches after static file changes. Useful for development and testing.
## All credit belongs to Usman Nasir
## To use make it executable
## chmod +x /usr/local/EagleEP/upgrade.sh
## Then run it like below.
## /usr/local/EagleEP/upgrade.sh

cd /usr/local/EagleEP && /usr/local/EagleEP/bin/python manage.py collectstatic --no-input
rm -rf /usr/local/EagleEP/public/static/*
cp -R  /usr/local/EagleEP/static/* /usr/local/EagleEP/public/static/
mkdir /usr/local/EagleEP/public/static/csf/
find /usr/local/EagleEP -type d -exec chmod 0755 {} \;
find /usr/local/EagleEP -type f -exec chmod 0644 {} \;
chmod -R 755 /usr/local/EagleEP/bin
chown -R root:root /usr/local/EagleEP
chown -R lscpd:lscpd /usr/local/EagleEP/public/phpmyadmin/tmp
systemctl restart lscpd
