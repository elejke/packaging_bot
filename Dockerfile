FROM elejke/python:3.8-alpine-zbar-lxml

WORKDIR /app

RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
RUN apk add build-base jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib

COPY requirements.txt /app/

RUN apk add libxml2-dev libxslt-dev
RUN apk add git
ENV ZBAR_PATH=/usr/lib/libzbar.so.0

RUN pip install -r requirements.txt

RUN pip uninstall pyzbar --yes
RUN pip install git+git://github.com/NaturalHistoryMuseum/pyzbar.git@feature/40-path-to-zbar

RUN apk add libzbar

COPY . /app/

RUN nohup python client/manage.py runserver

CMD python client/manage.py botpolling --username=open_recycle_team_bot
#CMD python bot.py
