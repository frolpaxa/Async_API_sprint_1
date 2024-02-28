from psycopg2._psycopg import cursor as Cursor

from backoff import backoff
from models import Movie, Genre, Person
from utils import transform_data


MAPPERS = {
    "movies": lambda x: Movie(**transform_data(x)),
    "genres": lambda x: Genre(**x),
    "persons": lambda x: Person(**x),
}


class PgLoader:
    """
    Класс для работы с PG
    """

    def __init__(self, cursor: Cursor, pack_size: int):
        self.cursor = cursor
        self.pack_size = pack_size

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
    def read_data(self, sql_query: str, modified: str, index: str):
        self.cursor.execute(sql_query.lower(), (modified,))

        while rows := self.cursor.fetchmany(self.pack_size):
            data = list()

            for row in rows:
                data.append(MAPPERS[index](row))

            yield data, rows[-1]["updated_at"]
