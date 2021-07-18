FROM python:3.8-slim

RUN apt-get update
RUN apt-get install -y python3-dev gcc

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD . /app
WORKDIR /app/

RUN chmod +x run.sh

ENV PYTHONPATH=/app
EXPOSE 3500
CMD ["/app/run.sh"]