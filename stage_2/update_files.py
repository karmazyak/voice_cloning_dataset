import os
import csv

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from utils import read_pickle, dump_pickle


class Configs:

    """
    Класс Configs содержит конфигурационные параметры для выполнения процесса идентификации говорящих.
    
    Атрибуты:
        FOLDER_PATH (str): Путь к директории с датасетом, содержащим аудиофайлы.
        speakers_file_path (str): Путь до CSV-файла с результатами распознавания спикеров.
        max_workers (int): Кол-во параллеобных потоков.
    """
    FOLDER_PATH = "/DATA/PICKLES/" #mount dir
    SAVE_RESULT_FOLDER = "/RESULTS/" #mount dir
    speakers_file_path = "speaker_data_all.csv"
    max_workers = 30


def process_file(
    file_name: str,
    gender: str,
    speaker_id: int
):
    """
    Обрабатывает один файл: добавляет данные по гендеру и идентификатору говорящего.

    :param file_name: Имя файла
    :param gender: Пол говорящего
    :param speaker_id: Идентификатор говорящего
    """
    full_file_name = os.path.join(Configs.FOLDER_PATH, file_name)
    data = read_pickle(full_file_name)
    data["gender"] = gender
    data["speaker_id"] = speaker_id
    dump_pickle(data, full_file_name)


def read_data(file_csv: str):
    """
    Читает данные из CSV файла и преобразует их в список.

    :param file_csv: Путь к CSV файлу
    :return: Список данных, где каждый элемент содержит имя файла, гендер и идентификатор говорящего
    """
    all_data = []
    with open(file_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for (file_name, gender, speaker_id) in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                all_data.append([file_name, gender, int(speaker_id)])
                line_count += 1
    return all_data


if __name__ == "__main__":
    all_data = read_data(
        os.path.join(
            Configs.SAVE_RESULT_FOLDER,
            Configs.speakers_file_path
        )
    )
    with ThreadPoolExecutor(max_workers=Configs.max_workers) as executor:
        futures = []
        with tqdm(total=len(all_data), desc="Processing files") as pbar:
            for file_name, gender, speaker_id in all_data:
                futures.append(executor.submit(process_file, file_name, gender, speaker_id))
            
            for future in as_completed(futures):
                future.result()
                pbar.update(1)
