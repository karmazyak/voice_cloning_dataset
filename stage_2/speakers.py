import csv
import re
import os
import random
import pickle
import librosa
import torchaudio
import torch
import numpy as np
import pandas as pd

from tqdm import tqdm
from glob import glob
from pyannote.audio import Pipeline, Inference, Model
from scipy.spatial.distance import cdist
from collections import defaultdict
from typing import List, Optional, Union, Dict, Literal


from utils import read_pickle
from filter.gender import GenderRecognition

class Configs:
    """
    Класс Configs содержит конфигурационные параметры для выполнения процесса идентификации говорящих.

    Атрибуты:
        HF_TOKEN (str): Токен для доступа к Hugging Face API, необходимый для загрузки моделей.
        FOLDER_PATH (str): Путь к директории с датасетом, содержащим аудиофайлы.
        device (str): Устройство для выполнения вычислений, например, "cuda:0" для использования GPU.
        embedds_mean_claster (int): Количество эмбеддингов, необходимое для подсчета среднего встраивания (эмбеддинга) для каждого говорящего.
        embedder_threshold (float): Пороговое значение для косинусного расстояния между эмбеддингами, используемое для определения новых говорящих.
        result_file_name (str): Имя CSV-файла для сохранения результатов распознавания.
        male_mean_emb_file_name (str): Имя файла для сохранения средних эмбеддингов мужчин.
        female_mean_emb_file_name (str): Имя файла для сохранения средних эмбеддингов женщин.
    """
    
    HF_TOKEN = "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"
    FOLDER_PATH = "/home/jovyan/dataset/"
    device = "cuda:0"
    embedds_mean_claster = 30
    embedder_threshold = 0.5
    result_file_name = "speaker_data_all.csv"
    male_mean_emb_file_name = "male_mean_embeddings.pkl"
    female_mean_emb_file_name= "female_mean_embeddings.pkl"

male_speaker_embeddings = []
female_speaker_embeddings = []
max_speaker_id = 1

model = Model.from_pretrained(
    "pyannote/embedding", 
    use_auth_token=Configs.HF_TOKEN
).to(Configs.device)
inference_embedder = Inference(model, window="whole")



def extract_sort_key(file_name: str):
    """
    Функция стравнения названия файлов.
    Функция для сортировки файлов по названию и индексу фрагмента аудио.
    Пример:
    [audio_12.pickle, audio_0.pickle, audio_2.pickle, audio_1.pickle] ->
    [audio_0.pickle, audio_1.pickle, audio_2.pickle, audio_12.pickle] ->
    
    :param file_name: Имя файла
    :return: Кортеж с базовым именем и индексом
    """
    match = re.search(r'_(\d+)\.pickle$', file_name)
    if match:
        base_name = file_name[:match.start()]
        index = int(match.group(1))
        return (base_name, index)
    else:
        return (file_name, 0)


def embedder_preocess_audio(audio: np.array, orig_sr: int = 24_000, device: str = "cpu"):
    """
    Обрабатывает аудиофайл, преобразуя его в моно, нормализуя и изменяя частоту дискретизации.
    
    :param audio: Аудио в формате numpy массива
    :param orig_sr: Исходная частота дискретизации аудиофайла
    :param device: Устройство для преобразования тензора (CPU или GPU)
    :return: Тензор аудиоданных
    """
    if np.issubdtype(audio.dtype, np.integer):
        audio = np.array(audio, dtype=float) / 32768.0
    if len(audio.shape) != 1:
        audio = audio.mean(axis=1) #create_mono_audio
    audio = librosa.resample(audio, orig_sr=orig_sr, target_sr=16_000)
    audio = torch.tensor(audio.reshape(1, -1), dtype=torch.float32).to(device)
    return audio

def get_embedding(audio: np.array, sample_rate: int = 16_000):
    """
    Вычисляет эмбеддинг аудио
    
    :param audio: Тензор аудио данных
    :param sample_rate: Частота дискретизации
    :return: Встраивание (эмбеддинг) аудио в виде numpy массива
    """
    embedding = inference_embedder(({
        "waveform": audio,
        "sample_rate": sample_rate
    })).reshape(1, 512)
    return embedding

def calculate_dist(emb1, emb2):
    """
    Вычисляет косинусное расстояние между двумя эмбеддингами.
    
    :param emb1: Встраивание 1
    :param emb2: Встраивание 2
    :return: Косинусное расстояние
    """
    return cdist(emb1, emb2, metric="cosine")

def update_mean_embedding(speaker_info: tuple, new_embed: np.array):
    """
    Обновляет среднее встраивание для говорящего, если собрано достаточно эмбеддингов.
    
    :param speaker_info: Кортеж информации о говорящем (среднее встраивание, id, все эмбеддинги, завершен ли процесс)
    :param new_embed: Новый эмбеддинг для обновления среднего
    :return: Обновленное среднее встраивание и статус завершенности
    """
    mean_embedding, speaker_id, all_embeddings, finalized = speaker_info
    if finalized:
        return speaker_info
    all_embeddings.append(new_embed)
    if len(all_embeddings) == Configs.embedds_mean_claster:
        mean_embedding = np.mean(all_embeddings, axis=0)
        finalized = True
        all_embeddings = [] # for memory saving
    elif len(all_embeddings) < Configs.embedds_mean_claster:
        mean_embedding = np.mean(all_embeddings, axis=0)
    return (mean_embedding, speaker_id, all_embeddings, finalized)

def assign_speaker(audio: np.array, gender: str):
    """
    Присваивает идентификатор говорящего на основе эмбеддингов и пола.

    :param audio: Обработанный аудиосигнал
    :param gender: Пол говорящего ('male' или 'female')
    :return: Идентификатор говорящего
    """
    global max_speaker_id, male_speaker_embeddings, female_speaker_embeddings
    
    new_embed = get_embedding(audio)
    
    if gender == "male":
        speaker_embeddings = male_speaker_embeddings
    else:
        speaker_embeddings = female_speaker_embeddings
    
    if not speaker_embeddings:
        speaker_embeddings.append((new_embed, max_speaker_id, [new_embed], False))
        assigned_id = max_speaker_id
        max_speaker_id += 1
        if gender == "male":
            male_speaker_embeddings = speaker_embeddings
        else:
            female_speaker_embeddings = speaker_embeddings
        return assigned_id

    distances = [calculate_dist(new_embed, speaker_emb) for speaker_emb, _, _, _ in speaker_embeddings]
    
    min_distance = min(distances)
    min_index = distances.index(min_distance)
    
    if min_distance > Configs.embedder_threshold:
        speaker_embeddings.append((new_embed, max_speaker_id, [new_embed], False))
        assigned_id = max_speaker_id
        max_speaker_id += 1
    else:
        speaker_embeddings[min_index] = update_mean_embedding(speaker_embeddings[min_index], new_embed)
        assigned_id = speaker_embeddings[min_index][1]
    
    if gender == "male":
        male_speaker_embeddings = speaker_embeddings
    else:
        female_speaker_embeddings = speaker_embeddings
    
    return assigned_id

def save_mean_embeddings(
    speaker_embeddings: tuple[np.array, int, List[np.array], bool],
    filename="speaker_mean_embeddings.pkl"):
    """
    Сохраняет mean эмбеддинги для спикеров.

    :param speaker_embeddings: Список всех эмбеддингов с данными о говорящем
    :param filename: Имя файла для сохранения
    """
    mean_embeddings = [(mean_emb, speaker_id) for mean_emb, speaker_id, _, _ in speaker_embeddings]
    with open(filename, 'wb') as f:
        pickle.dump(mean_embeddings, f)


if __name__ == "__main__":
    speakers_dict = defaultdict(list)
    files = [os.path.join(Configs.FOLDER_PATH, file_name) for file_name in os.listdir(Configs.FOLDER_PATH)]
    files.sort(key=extract_sort_key)
    genter_classifier_object = GenderRecognition()

    with open(Configs.result_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['file_name', 'gender', 'speaker_id'])
        for file_name in tqdm(files):
            audio = read_pickle(file_name)['audio']
            gender = genter_classifier_object.predict(audio=audio)  # "male" or "female"
            audio_processed = embedder_preocess_audio(audio=audio, device=Configs.device)
            speaker_id = assign_speaker(audio_processed, gender)
            speakers_dict[speaker_id].append(file_name)
            writer.writerow([os.path.basename(file_name), gender, speaker_id])


    save_mean_embeddings(male_speaker_embeddings, filename=Configs.male_mean_emb_file_name)
    save_mean_embeddings(female_speaker_embeddings, filename=Configs.female_mean_emb_file_name)
