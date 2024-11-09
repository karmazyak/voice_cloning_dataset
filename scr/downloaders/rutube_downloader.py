import requests
import os
import shutil
import subprocess
import librosa
import numpy as np

from scr.utils.audio_converters import ffmpeg_audio_converter
from tqdm import tqdm

HEADERS = {
    'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  '(KHTML, like Gecko) '
                  'Chrome/98.0.4758.132 YaBrowser/22.3.1.892 Yowser/2.5 Safari/537.36'),
    'accept': '*/*'
    }


def _sanitize_filename(filename: str) -> str:
    """
    Удаляет недопустимые символы из названия файла.
    """
    forbidden_chars = ["/", "\\", "[", "]", "?", "'", '"', ":", ".", "|"]
    for char in forbidden_chars:
        filename = filename.replace(char, "")
    return filename.replace(" ", "_")


def _get_video_info(video_id: str):
    """
    Получение автора, названия видео и ссылки на плейлист с вариантами видео
    в разных разрешениях (т.н. m3u8)
    при помощи обращения к апи рутуба по ссылке формата
    https://rutube.ru/api/play/options/{video_id}
    """
    url = f'https://rutube.ru/api/play/options/{video_id}'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        video_data = response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Ошибка запроса к Rutube API: {e}")

    video_author = _sanitize_filename(video_data['author']['name'])
    video_title = _sanitize_filename(video_data['title'])
    m3u8_link = video_data['video_balancer']['m3u8']

    return video_author, video_title, m3u8_link


def _get_download_links(m3u8_link):
    """
    Получение списка прямых ссылок на скачивание видео в разных разрешениях
    при помощи запроса
    к плейлисту по ссылке, полученной в _get_video_info
    """
    req = requests.get(url=m3u8_link, headers=HEADERS)
    req.raise_for_status()
    links = req.text.split('\n')
    return [links[i] for i in range(2, len(links), 2)]


def download_from_direct_link(direct_link, path_write, print_stats=True):
    if(print_stats):    
        subprocess.run(['ffmpeg', '-y', '-i', direct_link, path_write])
    else:
        subprocess.run(['ffmpeg', '-y', '-i', direct_link, path_write], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def download_rutube(url, output_dir, rate=None, print_stats=True, return_numpy=True):
    """
    Скачивание аудиодорожки из видео по ссылке на RuTube и сохранение в указанную директорию.

    Параметры:
    ----------
    url: str
        Ссылка на видео на RuTube.
    output_dir: str
        Директория для сохранения скачанного файла.
    rate: int, optional
        Частота дискретизации аудио. Если None, используется исходная частота аудиофайла.
    print_stats: bool, optional
        Если True, выводится информация о процессе загрузки (по умолчанию: True).
    return_numpy: bool, optional
        Если True, возвращает аудиофайл в формате NumPy массива. Если False, возвращает только метаданные (по умолчанию: True).

    Возвращает:
    -----------
    dict:
        Словарь с информацией о скачанном аудиофайле:
        - 'filename' (str): Название файла.
        - 'audio_path' (str): Путь к сохраненному аудиофайлу.
        - 'np_audio' (np.ndarray): Аудиоданные в формате NumPy, если `return_numpy=True`.
        - 'url' (str): Ссылка на исходное видео.
        - 'name' (str): Название видео.
        - 'chanel_name' (str): Имя автора.
        - 'time' (float): Длительность аудиофайла в секундах.
        - 'text' (None): Текст субтитров (не реализовано).
        - 'auto_text' (None): Флаг автоматических субтитров (не реализовано).
    """
    video_id = url.split("/")[-2]
    author, title, link_to_playlist = _get_video_info(video_id)
    download_links = _get_download_links(link_to_playlist)

    os.makedirs(output_dir, exist_ok=True)
    path_write = f'{output_dir}{title}.wav'
    print(f'Загрузка видео: {title}')
    download_from_direct_link(download_links[-1], path_write, print_stats=print_stats)
    print(f'Видео загружено: {title}')
    
    author_save = author[:25] + str(hash(author))
    title_save = title[:25] + str(hash(title))
    final_file_name = f'(Source:RuTube)(author:{author_save})(title:{title_save})'.replace(' ', '_')
    ffmpeg_audio_converter(path_write, output_dir, final_file_name, rate, 'wav')
    os.remove(path_write)
    del path_write
    audio_file_path = f'{output_dir}{final_file_name}.wav'

    temp_dict = {
            'filename': final_file_name,
            'audio_path': audio_file_path,
            'np_audio': None,
            'url': url,
            'name': title,
            'chanel_name': author,
            'time': librosa.get_duration(path=audio_file_path, sr=rate),
            'text': None,
            'auto_text': None
        }
    
    if(return_numpy):
        audio_numpy = librosa.load(audio_file_path, sr=rate)
        temp_dict['np_audio'] = audio_numpy[0]
        temp_dict['time'] = librosa.get_duration(y=audio_numpy[0], sr=audio_numpy[1])
        return temp_dict

    return temp_dict
    
    
