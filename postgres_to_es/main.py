from time import sleep
import contextlib
import psycopg2
from psycopg2.extras import RealDictCursor

from backoff import backoff
from configuration import Config
from es_uploader import EsUploader
from pg_loader import PgLoader
from queries import MOVIES, MOVIE_GENRES, MOVIE_PERSONS, GENRES, PERSONS
from state import JsonFileStorage, State

ENTITY = {
    "film_work": {"query": MOVIES, "index": "movies"},
    "person": {"query": MOVIE_PERSONS, "index": "movies"},
    "genre": {"query": MOVIE_GENRES, "index": "movies"},
    "genres": {"query": GENRES, "index": "genres"},
    "persons": {"query": PERSONS, "index": "persons"},
}


@backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
def run(conf: Config):
    try:
        with psycopg2.connect(dsn=conf.pg_dsn) as conn, conn.cursor(
            cursor_factory=RealDictCursor
        ) as cur:
            loader = PgLoader(cur, conf.pack_size)
            state = State(JsonFileStorage(file_path=conf.file_storage))
            modified = state.get_state("modified") or conf.start_date

            for i in ENTITY:
                uploader = EsUploader(conf.es_url, ENTITY[i]["index"])

                for data, last_updated in loader.read_data(
                    ENTITY[i]["query"], modified, ENTITY[i]["index"]
                ):
                    uploader.upload(data)

    finally:
        with contextlib.suppress(NameError):
            state.set_state("modified", str(last_updated))
            conn.close()
        sleep(conf.sleep_time)


if __name__ == "__main__":
    while True:
        run(Config())
