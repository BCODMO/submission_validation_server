#!/usr/bin/env bash
echo "password" | sudo -S service nginx start
echo "password" | sudo -S uwsgi --ini uwsgi.ini -s /tmp/uwsgi.socket
