web: gunicorn alx_backend_security.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A alx_backend_security worker --loglevel=info