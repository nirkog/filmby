if [ "$#" -gt 0 ]; then
	if [ "$1" = "-i" ]; then
		export IGNORE_CACHE=1
	fi
fi

flask --app ./server/ run -h 0.0.0.0 -p 80 --debug
