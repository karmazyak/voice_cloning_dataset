import pickle
import numpy as np
from os.path import isfile
from pathlib import Path
from typing import Union

class AudioFileSegment:
    """
    Класс для хранения аудиофайлов вместе с метаданными после транскрибации,
    содержащий в себе аудио файл в виде numpy массива,
    текст произнесенный в этом аудио и различные метаданные.
    
    Атрибуты:
    --------
    Основные (обязательные):
        - auidio_name: str — название исходного аудио (.wav) файла
        - audio_segmnet_index: int — индекс сегмента в исходном аудио файле
        - audio_segment_start: float — начало сегмента аудио в секундах
        - audio_segment_end: float — конец сегмента аудио в секундах
        - audio: np.ndarray — аудио в виде массива numpy
        - URL: str — ссылка на исходное видео
        - quality: int — оценка качества аудио от 1 до 3
        - name: str — название видео, аудио и тд
        - chanel_name: str — название канала (для видео)
        - auto_text: bool — флаг автоматических субтитров
        - text: str — субтитры
        - time: float — длина в секундах

    Дополнительные (необязательные):
        - gender: str — пол говорящего
        - speaker_id: int — ID говорящего
        - wada_snr_score: float — оценка соотношения сигнал/шум
        - old_text_transcription: str — старая версия текста транскрипции
        - number_of_speakers: int — количество говорящих

    Методы:
    --------
    save_pickle(file_path: str) -> bool:
        Сохраняет данные объекта в файл pickle.
    load(file_path: str) -> None:
        Загружает данные из файла pickle в текущий объект.
    load_pickle(file_path: str) -> AudioFileSegment:
        Загружает данные из файла pickle в новый объект класса и возвращает его.
    """

    REQUIRED_FIELDS = [
        "auidio_name", "audio_segmnet_index", "audio_segment_start", 
        "audio_segment_end", "audio", "URL", "quality", "name", 
        "chanel_name", "auto_text", "text", "time"
    ]
    OPTIONAL_FIELDS = [
        "gender", "speaker_id", "wada_snr_score", 
        "old_text_transcription", "number_of_speakers"
    ]

    def __init__(self, **kwargs):
        for field in self.REQUIRED_FIELDS:
            setattr(self, f"_{field}", kwargs[field])
        for field in self.OPTIONAL_FIELDS:
            setattr(self, f"_{field}", kwargs.get(field))

    def save_pickle(self, file_path: str) -> bool:
        """
        Сохраняет данные объекта в pickle.
        При необходимости создаются необходимые директории.
        Если данный файл уже существует, будет вызвано исключение FileExistsError.

        Параметры:
        -----------
        file_path: str
            Путь для созданного файла

        Пример использования:
            .save_pickle("my_object.pickle")

        Ошибки:
        --------
        PermissionError: если не хватает прав на создание файла.
        """
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        if isfile(file_path):
            raise FileExistsError(f"'{file_path}' already exists")

        data = {field: getattr(self, f"_{field}") for field in self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS}
        with open(file_path, 'wb') as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
        return True

    def load(self, file_path: str) -> None:
        """
        Загрузка данных из pickle в текущий объект.

        Параметры:
        -----------
        file_path: str
            Путь до файла для загрузки.
        
        Пример использования:
            X.load("object.pickle")
        
        Ошибки:
        --------
        FileNotFoundError: если файл не существует.
        """
        if not isfile(file_path):
            raise FileNotFoundError(f"'{file_path}' not found")
        
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        
        for field in self.REQUIRED_FIELDS:
            setattr(self, f"_{field}", data[field])
        for field in self.OPTIONAL_FIELDS:
            setattr(self, f"_{field}", data.get(field))

    @classmethod
    def load_pickle(cls, file_path: str) -> 'AudioFileSegment':
        """
        Загрузка данных в новый объект класса.

        Параметры:
        -----------
        file_path: str
            Путь до файла для загрузки.
        
        Пример использования:
            J = AudioFileSegment.load_pickle("object.pickle")
        
        Ошибки:
        --------
        FileNotFoundError: если файл не существует.
        """
        if not isfile(file_path):
            raise FileNotFoundError(f"'{file_path}' not found")
        
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        
        return cls(**data)

    def __getattr__(self, name):
        if name in self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS:
            return getattr(self, f"_{name}")
        raise AttributeError(f"'AudioFileSegment' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS:
            super().__setattr__(f"_{name}", value)
        else:
            super().__setattr__(name, value)
