FROM python:3.10

WORKDIR /elk

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY requirements.txt requirements.txt
COPY ./es_schemas/*.json /

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

RUN apt update && apt install netcat-traditional

COPY ./run.sh /
RUN chmod +x /run.sh
COPY . .

ENTRYPOINT ["/run.sh"]
