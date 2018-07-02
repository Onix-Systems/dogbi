FROM python:3.6


ADD . /

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT python manage.py collectstatic && gunicorn -b 0.0.0.0:8000 dog_bot.wsgi