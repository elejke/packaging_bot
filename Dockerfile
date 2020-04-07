FROM elejke/python:3.5-alpine-zbar

WORKDIR /app

RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
RUN apk add build-base jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

CMD python bot.py
