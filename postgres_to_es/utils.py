from models import PersonM


def transform_data(data):
    """
    Собираем необходимую структуру данных
    """

    actors = [
        PersonM(person_id=x["person_id"], person_name=x["person_name"])
        for x in data.get("persons")
        if x.get("person_role") == "actor"
    ]
    writers = [
        PersonM(person_id=x["person_id"], person_name=x["person_name"])
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
