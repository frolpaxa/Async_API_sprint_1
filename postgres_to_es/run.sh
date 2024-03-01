#!/usr/bin/env bash

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

while ! nc -z $ES_HOST $ES_PORT; do
  sleep 0.1
done

curl -XPUT $ES_URL"persons" -H 'Content-Type: application/json' -d /@es_persons.json
curl -XPUT $ES_URL"genres" -H 'Content-Type: application/json' -d /@es_genres.json
curl -XPUT $ES_URL"movies" -H 'Content-Type: application/json' -d /@es_movies.json

python main.py
