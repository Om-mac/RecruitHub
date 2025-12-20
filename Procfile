web: gunicorn auth_project.wsgi:application --log-file -
release: python manage.py migrate && python manage.py create_hr_user
