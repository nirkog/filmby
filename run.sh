#!/bin/bash

change_socket_permissions() {
	sleep 2
	chmod 777 filmby.sock
}

if [ "$#" -gt 0 ]; then
	if [ "$1" = "-i" ]; then
		export IGNORE_CACHE=1
	fi
fi

change_socket_permissions &
gunicorn --bind unix:filmby.sock -m 007 --pythonpath ./ server.wsgi:app --log-level DEBUG
# fg
# while true
# do
# 	sleep 10
# done
# gunicorn --log-level DEBUG --pythonpath src -b 0.0.0.0:443 server.wsgi:app --certfile /root/ssl/cert.pem --key /root/ssl/key.pem --ssl-version TLS_SERVER
# gunicorn --pythonpath src -b 0.0.0.0:443 server.wsgi:app --key /root/ssl/key.pem
