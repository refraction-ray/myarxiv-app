#! /bin/bash
# this script is a simple brute-force solution for database init delay when using docker-compose
sleep 60;
exec /usr/bin/supervisord -c /www/supervisor/supervisord.conf
