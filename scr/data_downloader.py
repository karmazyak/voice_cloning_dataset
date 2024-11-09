import os.path
import time
import threading
import traceback
import os, sys

from os.path import dirname

parent_directory = dirname(dirname(dirname(__file__)))
sys.path.append(parent_directory)


from scr.audio.audiofile import AudioFile
from scr.downloaders.youtube_downloader import download_youtube
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from scr.downloaders.vk_parser.parsing_vk import download_audio_vk_video
from scr.source_adapter import SourceAdapter


class DataDownloader:
    """
    Класс для управления процессом загрузки аудио/видео данных с различных источников.
    """
    def __init__(
            self,
            audios_folder: str,
            log_file_path: str,
            retry_sleep: float,
            max_retries: int,
            num_workers: int
    ) -> None:
        """
        Инициализация объекта DataDownloader.

        Параметры:
        ----------
        audios_folder: str
            Путь к папке, где будут сохраняться конечные аудиофайлы.
        log_file_path: str
            Путь к файлу, в который будут записываться логи.
        retry_sleep: float
            Время ожидания между попытками повторной загрузки.
        max_retries: int
            Максимальное количество попыток загрузки.
        num_workers: int
            Количество параллельных потоков для загрузки.
        """
        self.audios_folder = audios_folder
        self.log_file_path = log_file_path
        self.retry_sleep = retry_sleep
        self.max_retries = max_retries
        self.source_adapter = SourceAdapter()
        self.num_workers = num_workers
        self.lock = threading.Lock()
        
        if not os.path.exists(self.log_file_path):
            self.log_creation()

    def log_creation(self) -> None:
        """
        Метод для создания файла логов, если его не существует.
        """
        print(self.log_file_path)
        with open(self.log_file_path, 'w') as f:
            message = f'number, url, status\n'
            f.write(message)

    def log_insertion(self, status: str, url: str) -> None:
        """
        Метод для добавления новой записи в файл логов.

        Параметры:
        ----------
        status : str
            Статус загрузки данных.
        url: str
            URL-адрес аудиофайла.
        """
        with open(self.log_file_path) as f:
            for line in f:
                pass
        max_value = line.split(',')[0]
        if max_value == 'number':
            max_value = 0
        max_value = int(max_value) + 1
        with open(self.log_file_path, 'a') as f:
            message = f'{max_value}, {url}, {status}\n'
            f.write(message)

    def job_worker(self, url: str, source_type: str, quality: int = 1) -> None:
        """
        Метод для обработки и загрузки данных.

        Параметры:
        ----------
        url: str
            URL-адрес аудиофайла.
        source_type: {'youtube', 'vk', 'rutube'}
            Источник аудиофайла.
        quality: int
            Числовое представление качества аудиофайла, от 1 до 3. Enum AudioQuality
        """
        if source_type == 'youtube':
            folder = 'youtube'
        elif source_type == 'vk':
            folder = 'vk'
        elif source_type == 'rutube':
            folder = 'rutube'
        else:
            raise Exception('source_type was not matched')
        save_path = f'{self.audios_folder}/audio/{folder}/'

        attempts = 0
        downloaded_data = None
        while attempts < self.max_retries:
            try:
                downloaded_data = self.source_adapter.download(url, source_type, save_path)
                break
            except Exception as e:
                print(traceback.format_exc())
                print(f"Error downloading {url}: {e}")
                attempts += 1
                sleep(self.retry_sleep)

        if downloaded_data is not None:
            downloaded_data['quality'] = quality
            save_path_pickle = f'{self.audios_folder}/pickles/{folder}/{downloaded_data["filename"]}.pickle'
            try:
                audiofile = AudioFile(
                    audio_path=downloaded_data['audio_path'],
                    URL=downloaded_data['url'],
                    quality=downloaded_data['quality'],
                    name=downloaded_data['name'],
                    chanel_name=downloaded_data['chanel_name'],
                    auto_text=True if downloaded_data['auto_text'] == 'generated' else False,
                    text='' if downloaded_data['text'] is None else str(downloaded_data['text']),
                    time=downloaded_data['time']
                )                
                audiofile.save_pickle(save_path_pickle)
            except Exception as e:
                print(f"Error saving {url}: {e}")
            
            self.lock.acquire()
            self.log_insertion('GOOD', url)
            self.lock.release()
        else:
            self.lock.acquire()
            self.log_insertion('BAD', url)
            self.lock.release()
            print(f'{url=} is not valid')
        print(f"finished = {url}")

    def run(
            self,
            urls: list,
            sources: list,
            quality: list
    ) -> None:
        """
        Основной метод класса. Создает пул потоков с количеством потоков, определённым в __init__.

        Параметры:
        ----------
        urls: list[str]
            Список URL-адресов для загрузки.
        sources: list[str]
            Список источников загрузки.
        quality: list[str]
            Список, содержащий качество аудиофайлов.
        """
        with ThreadPoolExecutor(self.num_workers) as executor:
            executor.map(self.job_worker, urls, sources, quality)
