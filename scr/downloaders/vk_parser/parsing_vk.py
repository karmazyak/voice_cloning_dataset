import requests
import re
import os
import librosa
import vk_api
import yt_dlp
from typing import List, Union
from scr.downloaders.vk_parser.utils_parsing_vk import (
    captcha_handler, _get_chanel_name_by_id, suppress_stdout
)
from os.path import isfile


RE_VIDEO_PATTERN = re.compile(r'video[-]?([\d]+_[\d]+)')

def get_video_name(url: str) -> str:
    """
    Возвращает идентификатор видео из URL ВКонтакте.
    Пример:
        get_video_name("https://vk.com/video55155418_456241704") ->
        video55155418_456241704
    """
    match = re.search(RE_VIDEO_PATTERN, url)
    if match:
        name = url[match.start():match.end()]
    else:
        raise ValueError("Не найден индентификатор видео по ссылке")
    return name

def get_options(download_dir:str, file_name:str, sample_rate = 24000) -> dict:
    """
    Возвращает параметры для yt_dlp.YoutubeDL.
    Более подробно можно ознакомиться по ссылке 
    (https://github.com/yt-dlp/yt-dlp)
    """
    ydl_opts = {
        'extract_audio': True,
        # Download the best video available but no better than 144p,
        # or the worst video if there is no video under 144p
        'ie': "vk",
        'format': "bv*[height<=144]+ba/b[height<=144] / wv*+ba/w",
        'outtmpl': download_dir + file_name,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitle': '--write-sub --sub-lang ru',
        "retries": 10,
        "noplaylist": True,
        "restrictfilenames": True,
        "forcefilename": True,
        "simulate": False,
        # ℹ️ See help(yt_dlp.postprocessor) for a list
        # of available Postprocessors and their arguments
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192'
        }],
        'postprocessor_args': [
            '-ar', str(sample_rate),
            '-ac', '2'
        ]
    }
    return ydl_opts

def authentication() -> None:
    """
    Аутентификация в аккаунт ВКонтакте с использованием
    переменных окружения."""
    user_login = os.environ.get('API_VK_LOGIN')
    user_token = os.environ.get('API_VK_TOKEN')

    session = vk_api.VkApi(
        login=user_login,
        token= user_token,
        captcha_handler=None,
        config_filename=".vk_config.v2.json",
        api_version="5.92",
        app_id=2685278
    )

    try:
        session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(
        """
            Перед запуском скрипта установите переменные среды:
            export API_VK_LOGIN="..." #phone number
            export API_VK_PASSWORD="..." # пароль
            export API_VK_TOKEN="..." #token
        """
        )
        print("Ошибка аутентификации:", error_msg)
    return (True, session)

def _return_video_ids(video_ids: List[str]) -> List[str]:
    """
    Получая список идентификаторов видео в формате "video{owner_id}_{video_id}",
    возвращает список идентификаторов видео в формате "{owner_id}_{video_id}".
    """
    if not len(video_ids):
        return []
    video_ids_vals = [video_id.replace("video", "") for video_id in video_ids]
    return video_ids_vals

def _parsing_api_respond(server_respond: dict,
                        user_infos: dict,
                        groups_infos: dict) -> List:
    """
    Анализирует ответ сервера и возвращает список словарей, содержащих информацию о видео.
    Аргументы:
        server_respond (dict): Ответ от API-сервера ВК.
        user_infos (dict): словарь, содержащий информацию о пользователях.
        groups_infos (dict): словарь, содержащий информацию о группах.
    
    Возвраpащает  список словарей, содержащих информацию о видео.
    """
    resulrs = []
    for item in server_respond.get("items", {}):
        value_owner_id = item["owner_id"]
        value_video_id = item["id"]
        if item.get("live", None) == 1: # если данное видое это стрим, то пропускаем данную ссылку
            print(f"[INFO]: ERROR with video https://vk.com/video{value_owner_id}_{value_video_id}")
            resulrs.append(dict())
        elif item.get("type", None) == "music_video":
             #Видео не должен быть формат видео music_video.
            print(f"[INFO]: ERROR with video https://vk.com/video{value_owner_id}_{value_video_id}")
            resulrs.append(dict())
        else:
            owner_id = item.get("owner_id", None)
            chanel_name = _get_chanel_name_by_id(owner_id, user_infos, groups_infos)
            current_result = {
                "URL": f"https://vk.com/video{value_owner_id}_{value_video_id}",
                "video_name": item.get("title", None),
                "duration": item.get("duration", None),
                "player_link": item.get("player", None),
                "video_id": item.get("id", None),
                "owner_id": item.get("owner_id", None),
                "chanel_name": chanel_name,
                "type_video": item.get("type", None),
            }
            resulrs.append(current_result)
    return resulrs

def scrape_video_ids(session: vk_api.VkApi, video_ids: List[str]) -> List[dict]:
    """
    Собирает информацию о видео с заданными идентификаторами из ВК, используя предоставленную сессию.
    Аргументы:
        сеанс (vk_api.VkApi): аутентифицированный сеанс API ВКонтакте.
        video_ids (List[str]): список идентификаторов видео, информацию о которых нужно собрать.
    Возвращает список словарей, содержащих информацию о данных видео.
    """
    video_ids_vals = _return_video_ids(video_ids)

    headers = {
        "access_token": os.environ.get('API_VK_TOKEN'),
        "videos": ",".join(video_ids_vals),
        "extended": "1",
        "fields": "profiles, groups",
        "v": session.api_version,
    }
    req = requests.get("https://api.vk.com/method/video.get", headers)
    api_res = req.json()
    server_respond = api_res.get("response", {})
    user_infos = server_respond.get("profiles", [])
    groups_infos = server_respond.get("groups", [])

    resulrs = _parsing_api_respond(server_respond, user_infos, groups_infos)
    return resulrs

def parse_links_and_returnl_video_ids(video_urls: List[str]) -> List[str]:
    """
    Анализирует список URL-адресов с видео и возвращает список идентификаторов видео.
    video_urls (List[str]): список URL-адресов видео.
    Возвращает список идентификаторов видео.
    """
    video_ids = []
    for _, link in enumerate(video_urls):
        match = re.search(RE_VIDEO_PATTERN, link)
        if match:
            video_ids.append(link[match.start():match.end()])
    return video_ids

def get_subs(download_dir: str, dct: dict) -> (bool, str):
    flag_has_subtitels = "subtitels" in dct
    subtitles = ""
    if flag_has_subtitels:
        with open(dct['subtitels'], 'r') as file_:
            subtitles = file_.read()
    return (flag_has_subtitels, subtitles)

def download_YoutubeDL(resulrs: List[dict],
                       download_dir: str,
                       verbose: bool,
                       return_numpy: str = False,
                       target_sample_rate = 24_000
) -> None:
    """
    Скачивает видео с помощью yt_dlp и возвращает информацию о скачанном контенте.

    Параметры:
    ----------
    resulrs: List[dict]
        Список словарей с информацией о видео, которые нужно скачать.
    download_dir: str
        Директория, в которую будут сохранены скачанные файлы.
    verbose: bool
        Флаг для вывода подробной информации о процессе загрузки.
    return_numpy: bool, optional
        Возвращать ли аудиоданные в формате NumPy. По умолчанию False.
    target_sample_rate: int, optional
        Частота дискретизации аудио. По умолчанию 24000.

    Возвращает:
    -----------
    output_vals: List[dict]
        Список словарей, содержащих информацию о скачанных аудиофайлах:
        - 'filename' (str): Название файла.
        - 'audio_path' (str): Путь к сохраненному аудиофайлу.
        - 'np_audio' (np.ndarray, optional): Аудиоданные в формате NumPy (если return_numpy=True).
        - 'url' (str): Ссылка на исходное видео.
        - 'name' (str): Название видео.
        - 'chanel_name' (str): Имя автора канала.
        - 'time' (int): Длительность видео в секундах.
        - 'text' (str или None): Субтитры видео (если доступны).
        - 'auto_text' (str): Тип субтитров ('generated' — автоматически сгенерированные, 'empty' — отсутствуют).
    """
    output_vals = []
    for current_index in range(len(resulrs)):
        item = resulrs[current_index]
        if len(item) > 0:
            url = item["URL"]
            ydl_opts = get_options(download_dir, get_video_name(url),
                                   sample_rate=target_sample_rate)
            if verbose:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
            else:
                with suppress_stdout():
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
            file_name_wav = filename+".wav"
            file_name_subs = filename+".ru.vtt"
            if return_numpy:
                if isfile(file_name_wav):
                    item["np_audio"] = librosa.load(file_name_wav,
                                                    sr=target_sample_rate)[0]
                else:
                    raise ValueError()
            if isfile(file_name_subs):
                item["subtitels"] = file_name_subs

            item['audio_path'] = file_name_wav
            flag_has_subtitels, subtitles = get_subs(download_dir, item)
            if flag_has_subtitels:
                auto_text = 'generated'
            else:
                auto_text = 'empty'
                subtitles = None
            final_file_name  = "(Source:VkVideo)" + item["URL"].split('/')[-1]
            temp_dict = {
                "filename": final_file_name,
                "audio_path": item["audio_path"],
                "url": item["URL"],
                "name": item["video_name"],
                "auto_text": auto_text,
                "chanel_name": item["chanel_name"],
                "text": subtitles,
                "time": item["duration"],
            }
            if return_numpy:
                temp_dict["np_audio"] = item["np_audio"]
            output_vals.append(temp_dict)
            if isfile(file_name_subs):
                os.remove(file_name_subs)
        else:
            raise ValueError("atributs for audio not found")
        return output_vals

def download_audio_vk_video(urls: Union[str, List[str]],
                            download_dir:str,
                            verbose:bool,
                            target_sample_rate=24_000):
    """
    Загружает аудио из видеороликов ВК по их URL-адресам и сохраняет их в указанную директорию.

    Параметры:
    ----------
    urls: Union[str, List[str]]
        Строка или список строк, представляющих URL-адреса видео VK, с которых нужно скачать аудио.
    download_dir: str
        Каталог, в котором будут сохранены аудиофайлы и промежуточные файлы.
    verbose: bool
        Флаг для вывода подробной информации о процессе загрузки.
    target_sample_rate: int, optional
        Частота дискретизации аудио. По умолчанию 24000.

    Возвращает:
    -----------
    output_vals: List[dict]
        Список словарей, содержащих информацию о скачанных аудиофайлах.
    """
    print("Start downloading: ", urls)
    output_vals = None
    if type(urls) == str:
        urls = [urls]
    elif type(urls) != list:
        raise ValueError
    if download_dir[-1] != "/":
        download_dir += "/"
    status, session = authentication()
    if status:
        video_ids = parse_links_and_returnl_video_ids(urls)
        if video_ids == []:
            raise ValueError("Не найдено видео по данной ссылке")
        resulrs = scrape_video_ids(session=session, video_ids=video_ids)
        if len(resulrs) == 0:
            raise ValueError("Не найдено видео по данной ссылке")
        elif 0 < len(resulrs) < len(urls):
            raise ValueError("Не все ссылки валидны")
        output_vals = download_YoutubeDL(resulrs, download_dir, verbose, target_sample_rate=target_sample_rate)
    else:
        print("Bad login in vk API")
        raise Exception
    return output_vals
