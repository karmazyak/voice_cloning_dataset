import numpy as np
from enum import Enum

class AudioQuality(Enum):
    """
    Перечисление для хранения оценки качества аудио
    """
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class AudioFileBase:
    """
    Базовый класс для хранения информации о аудиофайле.
    Содержит методы для проверки типов данных.
    """
    @classmethod
    def verifiy_bool(cls, value, attribute_name) -> None:
        """
        Проверка на bool.
        """
        if type(value) != bool:
            error_text = f"{attribute_name} should be bool"
            raise ValueError(error_text)
        
    @classmethod
    def verifiy_quality(cls, value, attribute_name) -> None:
        """
        Проверка, что данное значение является числом от 1 до 3 или
        перечислением (enum) AudioQuality
        Union[AudioQuality, int]
        """
        if not (type(value) == AudioQuality or
            type(value) == int and value in {1,2,3}):
            error_text = (
            """quality should be Union[AudioQuality, int],
            int value one of  in{1,2,3}""")
            raise ValueError(error_text)

    @classmethod
    def verifiy_str(cls, value, attribute_name) -> None:
        """
        Проверка, на str.
        """
        if type(value) != str:
            error_text = f"{attribute_name} should be string"
            raise ValueError(error_text)

    @classmethod
    def verifiy_numeric(cls, value, attribute_name) -> None:
        """
        Проверка, на число.
        """
        if not isinstance(value, (int, float)):
            error_text = f"{attribute_name} should be int or float"
            raise ValueError(error_text)

    @classmethod
    def verifiy_numpy(cls, value, attribute_name) -> None:
        """
        Проверка, на массив numpy.
        """
        if type(value) != np.ndarray:
            error_text = f"{attribute_name} should be np.ndarray"
            raise ValueError(error_text)
