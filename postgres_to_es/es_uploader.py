import json

import requests

from backoff import backoff


class EsUploader:
    """
    Класс для работы с ELK
    """

    def __init__(self, url, index):
        self.url = url
        self.index = index

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
    def upload(self, data: list):
        data_list = list()

        for i in data:
            data_list.append(json.dumps({"index": {"_index": self.index, "_id": i.id}}))
            data_list.append(i.json())

        data = "\n".join(data_list)
        data += "\n"

        requests.post(
            self.url + "_bulk",
            headers={"Content-Type": "application/json; charset=utf-8"},
            data=data.encode("utf-8"),
        )
