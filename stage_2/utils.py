import pickle

def dump_pickle(pickle_data: dict, pickle_path: str):
    """
    Сохраняет данные в формате pickle.

    :param pickle_data: Словарь с данными для сохранения
    :param pickle_path: Путь к файлу для сохранения данных
    """
    with open(pickle_path, 'wb') as handle:
        pickle.dump(pickle_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def read_pickle(file_name: str):
    """
    Читает данные из pickle файла.

    :param file_name: Имя файла, из которого будут загружены данные
    :return: Данные, загруженные из файла
    """
    with open(file_name, "rb") as f:
        return pickle.load(f)
