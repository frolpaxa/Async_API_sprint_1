from models import PersonShort


def transform_movie_data(data):
    """
    Собираем необходимую структуру данных для фильмов
    """

    actors = [
        PersonShort(person_id=x["person_id"], person_name=x["person_name"])
        for x in data.get("persons")
        if x.get("person_role") == "actor"
    ]
    writers = [
        PersonShort(person_id=x["person_id"], person_name=x["person_name"])
        for x in data.get("persons")
        if x.get("person_role") == "writer"
    ]

    return data | dict(
        title=data.get("title"),
        description=data.get("description"),
        director=" ".join(
            [
                x.get("person_name")
                for x in data.get("persons")
                if x.get("person_role") == "director"
            ]
        ).strip(),
        actors_names=" ".join([person.name for person in actors]),
        writers_names=[person.name for person in writers],
        actors=actors,
        writers=writers,
    )


def transform_person_data(data):
    """
    Собираем необходимую структуру данных для персон
    """

    films = []

    for i in data["films"]:
        if i not in films:
            films.append(
                {
                    "id": i["id"],
                    "roles": [x["role"] for x in data["films"] if x["id"] == i["id"]],
                }
            )

    return dict(id=data["id"], full_name=data["full_name"], films=films)
