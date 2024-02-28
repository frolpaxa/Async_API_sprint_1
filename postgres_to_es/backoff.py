import logging
import time
from functools import wraps


def backoff(start_sleep_time, factor, border_sleep_time):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :return: результат выполнения функции
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            t = start_sleep_time
            counter = 1

            while True:
                try:
                    time.sleep(t)
                    result = func(*args, **kwargs)
                    break
                except Exception as ex:
                    logging.error(f"{ex}. Attempt: {counter}. Wait: {t} sec.")
                    t = min(t * 2**factor, border_sleep_time)
                    counter += 1

            return result

        return wrapper

    return decorator
