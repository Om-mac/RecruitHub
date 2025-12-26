release: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py create_superuser_from_env
web: gunicorn auth_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --timeout 120 --graceful-timeout 30 --keep-alive 5 --access-logfile - --error-logfile -
