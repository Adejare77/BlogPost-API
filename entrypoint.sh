set -e

python manage.py migrate

exec gunicorn blogPost.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 30 \
    --keep-alive 2 \
    --capture-output \
    --reload
