release: flask db upgrade
web: gunicorn riddle_me_this.app:create_app\(\) -b 0.0.0.0:$PORT -w 3
