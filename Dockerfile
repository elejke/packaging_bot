# FROM python:3.5-alpine
FROM thatsarr/alpine_armv7l-opencv

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

CMD python bot.py
