if [ "$#" -gt 0 ]; then
	if [ "$1" = "-i" ]; then
		export IGNORE_CACHE=1
	fi
fi

gunicorn --pythonpath src -b 0.0.0.0:443 server.wsgi:app --certfile /root/ssl/cert.pem --key /root/ssl/key.pem
