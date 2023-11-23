FROM python:3.11.2

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    redis  \
    ffmpeg \
    build-essential

RUN pip install setuptools

RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app
COPY downloads /app/downloads

CMD ["python", "run.py"]

