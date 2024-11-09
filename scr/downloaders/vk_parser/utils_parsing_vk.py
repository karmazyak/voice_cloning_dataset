from contextlib import contextmanager
from typing import List
import os
import sys

def captcha_handler(captcha):
    print("WARNING: CAPTCHA DETECTED!")
    key = input(
        f"CAPTCHA DETECTED, please solve it and input the solution. url= {captcha.get_url()} :"
    ).strip()
    return captcha.try_again(key)


def _get_user_info(user_id:int, lst_user_info:List[dict]):
    """
    Возвращает информацию о пользователе по его ID.

    Параметры:
    ----------
    user_id: int
        Идентификатор пользователя.
    lst_user_info: List[dict]
        Список словарей с информацией о пользователях.

    Возвращает:
    -----------
    str или None
        Имя и фамилия пользователя, если ID найден, иначе None.
    """
    result = None
    for value in lst_user_info:
        curr_user_id = value.get("id")
        if curr_user_id == user_id:
            result = f'{value.get("first_name")} {value.get("last_name")}'
            return result
    return None

def _get_group_info(group_id:int, lst_group_info: List[dict]):
    """
    Возвращает информацию о группе по её ID.

    Параметры:
    ----------
    group_id: int
        Идентификатор группы.
    lst_group_info: List[dict]
        Список словарей с информацией о группах.

    Возвращает:
    -----------
    str или None
        Название группы, если ID найден, иначе None.
    """

    group_id = abs(group_id) # group_id should be > 0
    result = None
    for items in lst_group_info:
        curr_user_id = items.get("id")
        if curr_user_id == group_id:
            result = f'{items.get("name")}'
            return result
    return None

def _get_chanel_name_by_id(owner_id:int, user_infos:List[dict], groups_infos:List[dict]):
    """
    Возвращает имя канала (пользователя или группы) по его идентификатору.

    Параметры:
    ----------
    owner_id: int
        Идентификатор владельца канала (положительное значение для пользователей, отрицательное для групп).
    user_infos: List[dict]
        Список информации о пользователях.
    groups_infos: List[dict]
        Список информации о группах.

    Возвращает:
    -----------
    str
        Имя канала (пользователя или группы).

    Исключения:
    -----------
    AttributeError
        Выбрасывается, если owner_id невалиден.
    """
    chanel_name = None
    if owner_id != None:
        if owner_id > 1:
            chanel_name = _get_user_info(owner_id, user_infos)
        elif owner_id < 0:
            chanel_name = _get_group_info(owner_id, groups_infos)
        else:
            raise AttributeError()
    else:
        raise AttributeError()
    return chanel_name

@contextmanager
def suppress_stdout():
    """
    Контекстный менеджер для подавления вывода в stdout.
    # https://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/

    Примечание:
    ----------
    Используется для отключения вывода сообщений yt_dlp, которые не уважают флаг quiet=True
    и выводят информацию о файлах в консоль.

    Пример:
    -------
    with suppress_stdout():
        some_function_with_loud_output()
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
