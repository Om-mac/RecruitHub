release: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py create_superuser
web: gunicorn auth_project.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --worker-class sync --timeout 600 --access-logfile -
