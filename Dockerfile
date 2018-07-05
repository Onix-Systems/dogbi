FROM python:3.6


ADD requirements.txt /requirements.txt
RUN pip install -r requirements.txt

ADD . /

EXPOSE 8000
RUN python telegram_bot/config.py
ENTRYPOINT python manage.py collectstatic && gunicorn -b 0.0.0.0:8000 dog_bot.wsgi
