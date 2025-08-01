FROM python:3.8.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
RUN mkdir -p /app/media /app/downloads /app/staticfiles
EXPOSE 8000
CMD ["gunicorn", "torrent_downloader.wsgi:application", "--bind", "0.0.0.0:8000"]
