import numpy as np

def pcm2float(sig, dtype='float32'):
    """
    Преобразует сигнал PCM в плавающий формат с диапазоном значений от -1 до 1.

    Args:
        sig (array_like): Входной массив, содержащий PCM-сигнал (должен быть целочисленным типом данных).
        dtype (str or np.dtype, optional): Тип данных для результата. По умолчанию 'float32', может быть 'float64' для двойной точности.

    Raises:
        TypeError: Если входной сигнал не является массивом целых чисел.
        TypeError: Если указанный тип данных результата не является типом с плавающей точкой.

    Returns:
        numpy.ndarray: Нормализованный сигнал с плавающей точкой с диапазоном значений от -1 до 1.

    See Also:
        float2pcm: Обратное преобразование плавающего сигнала в PCM.
        numpy.dtype: Для преобразования типов данных.

    Notes:
        - Нормализация сигнала происходит путем масштабирования значений от -1 до 1 относительно максимального значения типа данных.
        - Входной сигнал должен быть представлен целочисленным массивом, например, с типами 'int16', 'int32' и т.д.
    """
    sig = np.asarray(sig)
    if sig.dtype.kind not in 'iu':
        raise TypeError("'sig' must be an array of integers")
    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("'dtype' must be a floating point type")

    i = np.iinfo(sig.dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig.astype(dtype) - offset) / abs_max


def float2pcm(sig, dtype='int16'):
    """
    Преобразует сигнал с плавающей точкой (с диапазоном от -1 до 1) обратно в PCM.

    Args:
        sig (array_like): Входной массив, содержащий сигнал с плавающей точкой.
        dtype (str or np.dtype, optional): Тип данных для результата. По умолчанию 'int16', может быть, например, 'int32'.

    Raises:
        TypeError: Если входной сигнал не является массивом с плавающей точкой.
        TypeError: Если указанный тип данных результата не является целочисленным типом.

    Returns:
        numpy.ndarray: Целочисленный массив данных, масштабированный и обрезанный в диапазоне, определенном *dtype*.

    See Also:
        pcm2float: Преобразование сигнала PCM в плавающий формат.
        numpy.dtype: Для преобразования типов данных.

    Notes:
        - Значения за пределами диапазона [-1.0, 1.0) будут обрезаны.
        - Осуществляется масштабирование и преобразование типа данных на основе диапазона целочисленных значений.
        - Преобразование не включает добавление шума (дизеринг).
    """
    sig = np.asarray(sig)
    if sig.dtype.kind != 'f':
        raise TypeError("'sig' must be a float array")
    dtype = np.dtype(dtype)
    if dtype.kind not in 'iu':
        raise TypeError("'dtype' must be an integer type")

    i = np.iinfo(dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig * abs_max + offset).clip(i.min, i.max).astype(dtype)
