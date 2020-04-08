FROM elejke/python:3.8-alpine-zbar

WORKDIR /app

RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
RUN apk add build-base jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib

COPY requirements.txt /app/

RUN apk add libxml2-dev libxslt-dev
RUN apk add git
ENV ZBAR_PATH=/usr/lib/libzbar.so.0

RUN pip install -r requirements.txt

RUN pip install git+git://github.com/NaturalHistoryMuseum/pyzbar.git@feature/40-path-to-zbar

COPY . /app/

CMD python bot.py
