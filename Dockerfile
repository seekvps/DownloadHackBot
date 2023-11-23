FROM python:3.11.2-alpine As compile-image

WORKDIR /app

COPY requirements.txt /app/

RUN apk add --no-cache --virtual ffmpeg redis libpq-dev \
     && pip install --trusted-host pypi.python.org -r requirements.txt \
     && apk del .build-deps && rm -rf requirements.txt \

FROM python:3.11.2-alpine As runtime-image

WORKDIR /app


COPY .env run.py /app/
COPY app /app/app

CMD ["python", "run.py"]

