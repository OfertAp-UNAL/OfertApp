FROM python:3.11

RUN apt-get update

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

CMD /bin/bash -c python manage.py migrate && python manage.py runserver