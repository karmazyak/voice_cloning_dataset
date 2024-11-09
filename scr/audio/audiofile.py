import pickle

from typing import Union
from os.path import isfile
from pathlib import Path
from .baseaudiofile import AudioQuality, AudioFileBase


class AudioFile(AudioFileBase):
    """
    Данный класс предназначен для хранения аудиофайлов

    Атрибуты:
    --------
    audio_path: str
        Путь до аудио файла
    URL: str
        Ссылка на видео
    quality: Union[AudioQuality, int]
        Оценка качества аудио (1-3 или enum AudioQuality), где 1 ниалучшее качество.
    name: str
         Название видео, аудио и тд
    chanel_name: str
        Название канала (для видео)
    auto_text: bool
        Субтитры ручные или сгенерированы автоматически (флаг автоматических)
        True означает, что субтитры сгенерированы автоматически
    text: str
        субтитры
    time: float 
        Длина в сек

    Методы:
    --------
    save_pikle(self, file_path: str)
        Сохраняет данные объекта в pickle.
    def load(self, file_path: str):
        Загрузка данных из pickle в текущий объект.
    load_pickle(cls, file_path: str) -> AudioFile
        Загрузка данных в новый объект класса.
    """
    def __init__(self, audio_path : str, URL: str, quality:
            Union[AudioQuality, int],
            name: str, chanel_name: str, auto_text: bool,
            text: str, time: float) -> None:
        """
        Проверяет входные параметры и устанавливает все необходимые
        атрибуты для объекта AudioFile

        Параметры:
        --------
        audio_path: str
            Путь до аудио файла
        URL: str
            Ссылка на видео
        quality: Union[AudioQuality, int]
            Оценка качества аудио (1-3 или enum AudioQuality), где 1 ниалучшее качество.
        name: str
            Название видео, аудио и тд
        chanel_name: str
            Название канала (для видео)
        auto_text: bool
            Субтитры ручные или сгенерированы автоматически (флаг автоматических)
            True означает, что субтитры сгенерированы автоматически
        text: str
            субтитры
        time: float 
            Длина в сек
        """
        self.verifiy_str(audio_path, "audio_path")
        self.verifiy_str(URL, "URL")
        self.verifiy_quality(quality, "quality")
        self.verifiy_str(name, "name")
        self.verifiy_str(chanel_name, "chanel_name")
        self.verifiy_bool(auto_text, "auto_text")
        self.verifiy_str(text, "text")
        self.verifiy_numeric(time, "time")

        self.__audio_path = audio_path
        self.__URL = URL
        self.__quality = quality
        self.__name = name
        self.__chanel_name = chanel_name
        self.__auto_text = auto_text
        self.__text = text
        self.__time = time


    def save_pickle(self, file_path: str) -> True:
        """
        Сохраняет данные объекта в pickle.
        При необходимости создаются необходимые директории.
        Если данный файл уже существует, старый файл будет потерян.

        Агрументы:
        -------
        file_path: str
            Путь для сохранения файла
        -------
        Пример использования:
            obj.save_pickle("my_object.pickle")
        """
        parent_path = Path(file_path).parent
        parent_path.mkdir(parents=True, exist_ok=True)
        try:
            with open(file_path, 'wb') as file:
                pickle.dump(obj={
                    "audio_path": self.__audio_path,
                    "URL": self.__URL,
                    "quality": self.__quality,
                    "name": self.__name,
                    "chanel_name": self.__chanel_name,
                    "auto_text": self.__auto_text,
                    "text": self.__text,
                    "time": self.time
                }, file= file,
                protocol=pickle.HIGHEST_PROTOCOL)
        except PermissionError as e:
            print(f"Permission denied: {e}")
            raise e 
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
        return True
            
    

    def load(self, file_path: str):
        """
        Загрузка данных из pickle в текущий объект.

        -----
        Агрументы:
        file_path: str
            Путь до файла для загрузки.
            Вызывает ValueError: если файл не существует.
        -----
        Пример использования:
            X.load("object.pickle")
        """
        if not isfile(file_path):
            raise FileNotFoundError(f"'{file_path}' file doesn't exist")
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        self.audio_path = data["audio_path"]
        self.URL = data["URL"]
        self.quality = data["quality"]
        self.name = data["name"]
        self.chanel_name = data["chanel_name"]
        self.auto_text = data["auto_text"]
        self.text = data["text"]
        self.time = data["time"]

    @classmethod
    def load_pickle(cls, file_path: str):
        """
        Загрузка данных в новый объект класса.

        -----
        Агрументы:
        file_path: str
            Путь до файла для загрузки.
            Вызывает ValueError: если файл не существует.
        -----
        Пример использования:
            J = AudioFile.load_pickle("object.pickle")
        """
        if not isfile(file_path):
            raise ValueError(f"'{file_path}' file doesn't exist")
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        return cls(
                   data["audio_path"],
                   data["URL"],
                   data["quality"],
                   data["name"],
                   data["chanel_name"],
                   data["auto_text"],
                   data["text"],
                   data["time"],)

    @property
    def audio_path(self) -> str:
        return self.__audio_path
    
    @audio_path.setter
    def audio_path(self, audio_path: str) -> None:
        self.verifiy_str(audio_path, "audio_path")
        self.__audio_path = audio_path

    @property
    def URL(self) -> str:
        return self.__URL
    
    @URL.setter
    def URL(self, URL: str) -> None:
        self.verifiy_str(URL, "URL")
        self.__URL = URL
    
    @property
    def quality(self) -> AudioQuality:
        return self.__quality
    
    @quality.setter
    def quality(self, quality: Union[AudioQuality, int]) -> None:
        self.verifiy_quality(quality, "quality")
        if type(quality) == AudioQuality:
            self.__quality = quality
        else:
            self.__quality = AudioQuality(quality)

    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, name: str) -> None:
        self.verifiy_str(name, "name")
        self.__name = name
    
    @property
    def chanel_name(self) -> str:
        return self.__chanel_name
    
    @chanel_name.setter
    def chanel_name(self, chanel_name: str) -> None:
        self.verifiy_str(chanel_name, "chanel_name")
        self.__chanel_name = chanel_name
    
    @property
    def auto_text(self)  -> bool:
        return self.__auto_text
    
    @auto_text.setter
    def auto_text(self, auto_text : bool) -> None:
        self.verifiy_bool(auto_text, "auto_text")
        self.__auto_text = auto_text
    
    @property
    def text(self) -> str:
        return self.__text
    
    @text.setter
    def text(self, text: str) -> None:
        self.verifiy_str(text, "text")
        self.__text = text
    
    @property
    def time(self) -> float:
        return self.__time

    @time.setter
    def time(self, time: float) -> None:
        self.verifiy_numeric(time, "time")
        self.__time = time
