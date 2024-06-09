FROM python:3.9-slim

RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /avalance

COPY . /avalance/

RUN pip install -r requirements.txt

RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations --noinput
# RUN python manage.py migrate --noinput #