import os
import re
import torch
import librosa
import numpy as np
import whisper_timestamped as whisper
import multiprocessing
import random

from whisper.model import disable_sdpa
from pyannote.audio import Pipeline
from jiwer import cer
from tqdm import tqdm

from filter.snr_filter import calculate_wada_snr
from utils import read_pickle, dump_pickle


class Configs:
    """
    Класс Configs содержит конфигурационные параметры для запуска фильтрации аудиофайлов. 

    Атрибуты:
        HF_TOKEN (str): Токен для доступа к Hugging Face API, используется для загрузки моделей.
        path_pickles (str): Путь к директории, где хранятся pickle файлы с аудиоданными.
        path_bad_cuts (str): Путь к директории для хранения файлов, которые не прошли фильтрацию.
        whisper_model_name (str): Название модели Whisper для транскрибирования аудио.
        device (str): Устройство для выполнения вычислений, например, "cuda:0" для использования GPU.
        wada_snr_score_filter (int): Пороговое значение уровня соотношения сигнал-шум (SNR) для фильтрации аудио.
        cer_thresh (float): Порог для коэффициента ошибок символов (CER) для фильтрации транскрипций.
    """
    # Необходимо получить доступ к моделям pyannote (pyannote/speaker-diarization-3.1) на странице HF.
    # You need to agree to share your contact information to access this model (pyannote/speaker-diarization-3.1).
    HF_TOKEN = "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"
    path_pickles = '/DATA/PICKLES/' # Не менять. Необходимо изменить target в --mount папке при запуске docker run.
    path_bad_cuts = '/DATA/BAD_CUTS/' # Не менять. Необходимо изменить target в --mount папке при запуске docker run.
    whisper_model_name = "turbo"
    device = "cuda:1"
    wada_snr_score_filter = 20
    cer_thresh = 0.10


class Filter:
    def __init__(
        self,
        path_pickles,
        path_bad_cuts,
        filenames=None,
        cer_thresh=0.10,
        device="cuda",
        wada_snr_score_filter=20
    ):
        """
        Инициализирует класс фильтрации с заданными параметрами.

        :param path_pickles: Путь к директории с файлами pickle
        :param path_bad_cuts: Путь к директории для сохранения отбракованных файлов
        :param filenames: Список имен файлов для обработки
        :param cer_thresh: Пороговый уровень CER для фильтрации
        :param device: "cpu" или  "gpu"
        :param wada_snr_score_filter: Пороговый уровень SNR для фильтрации
        """
        self.filenames = filenames
        self.path_pickles = path_pickles
        os.makedirs(path_bad_cuts, exist_ok=True)
        self.device = device
        self.path_bad_cuts = path_bad_cuts
        self.model_whisper = whisper.load_model(
            Configs.whisper_model_name,
            device=device
        )
        self.cer_thresh = cer_thresh
        self.wada_snr_score_filter = wada_snr_score_filter


        self.pipeline_number_speakers = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=Configs.HF_TOKEN
        )
        self.pipeline_number_speakers.to(torch.device(device))


    def get_new_transcription(self, audio, orig_sr=24_000):
        """
        Создает новую транскрипцию для аудиофайла.

        :param audio: Аудио данные
        :param orig_sr: Исходная частота дискретизации аудио
        :return: Текст новой транскрипции
        """

        if np.issubdtype(audio.dtype, np.integer):
            audio = np.array(audio, dtype=float) / 32768.0
        if len(audio.shape) != 1:
            audio = audio.mean(axis=1)
        audio = librosa.resample(audio, orig_sr=orig_sr, target_sr=16_000)
        audio = torch.tensor(audio, dtype=torch.float32).to(self.device)
        transcribed = whisper.transcribe(
            self.model_whisper, 
            audio, 
            language="ru", 
            detect_disfluencies=False,
            beam_size=5,
            best_of=5, 
            temperature = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
            verbose=False
        )
        return transcribed['text']
    
    def get_number_of_speakers(self, audio, orig_sr=24_000):
        """
        Определяет количество говорящих в аудиофайле.

        :param audio: Аудио данные
        :param orig_sr: Исходная частота дискретизации аудио
        :return: Количество говорящих
        """
        if np.issubdtype(audio.dtype, np.integer):
            audio = np.array(audio, dtype=float) / 32768.0
        if len(audio.shape) != 1:
            audio = audio.mean(axis=1) #create_mono_audio
        audio = librosa.resample(audio, orig_sr=orig_sr, target_sr=16_000)
        audio = torch.tensor(
            audio.reshape(1, -1), dtype=torch.float32
        ).to(self.device)
        diarization = self.pipeline_number_speakers({
            "waveform": audio,
            "sample_rate": 16_000
        })
        return len(diarization.labels())

    
    def refactor_pickle(self, filename):
        """
        Фильтрация данных pickle файла на основе фильтров SNR и CER.

        :param filename: Имя файла для обработки
        """
        data = read_pickle(os.path.join(self.path_pickles, filename))
        if data.get("precessed", False):
            return
        #Calculate wads_snr score
        wada_snr_score = calculate_wada_snr(data['audio'])
        data['wada_snr_score'] = wada_snr_score
        #Calc number of speakers in audio
        number_of_speakers = self.get_number_of_speakers(data['audio'])
        data['number_of_speakers'] = number_of_speakers
        
        if wada_snr_score < self.wada_snr_score_filter or number_of_speakers > 1:
            data["rejected"] = True # the audio was thrown out
            # save new pikle file with updated data and delete original file
            print("REMOVING PIKLE")
            dump_pickle(data, os.path.join(self.path_bad_cuts, filename))
            os.remove(os.path.join(self.path_pickles, filename))
            return
        # Удаляем из текста транскрипции служебные символ для обозначения disfluencies [*]
        new_transcription = self.get_new_transcription(data["audio"]).replace("[*]", "")
        # Заменяем два и более пробела на один
        new_transcription = re.sub(r'\s+', ' ', new_transcription).strip()
        # Удаляем из текста транскрипции служебные символ для обозначения disfluencies [*]
        old_transcription = data['text'].replace("[*]", "")
        # Заменяем два и более пробела на один
        old_transcription = re.sub(r'\s+', ' ', old_transcription).strip()
        cer_rate = cer(old_transcription.lower(), new_transcription.lower())
        if cer_rate > self.cer_thresh:
            data["old_text_transcription"] = old_transcription
            data["text"] = new_transcription
            print(f'cer: {cer_rate}\n old_transcription: {old_transcription}\n new_transcribed: {new_transcription}')
        data["precessed"] = True
        dump_pickle(data, os.path.join(self.path_pickles, filename))
        
        
    def run(self):
        """
        Запускает процесс фильтрации файлов.
        """
        if self.filenames is None:
            for filename in tqdm(os.listdir(self.path_pickles)):
                self.refactor_pickle(filename)
        else:
            for filename in tqdm(self.filenames):
                self.refactor_pickle(filename)



def run(path_pickles, path_bad_cuts, filenames=None):
    """
    Запускает фильтрацию с заданными параметрами.
    
    :param path_pickles: Путь к директории с файлами pickle
    :param path_bad_cuts: Путь к директории для сохранения отбракованных файлов
    :param filenames: Список имен файлов для обработки (опционально)
    """
    if filenames is None:
            filenames = os.listdir(path_pickles)
    r = Filter(
        path_pickles,
        path_bad_cuts,
        filenames=filenames,
        cer_thresh=Configs.cer_thresh,
        device=Configs.device,
        wada_snr_score_filter = Configs.wada_snr_score_filter
    )
    r.run()
    print('Done')



def _run_parallel(path_pickles, path_bad_cuts, filenames):
    """
    Запускает фильтрацию в 1 поток
    
    :param path_pickles: Путь к директории с файлами pickle
    :param path_bad_cuts: Путь к директории для сохранения отбракованных файлов
    :param filenames: Список имен файлов для обработки (опционально)
    """
    r = Filter(
        path_pickles,
        path_bad_cuts,
        filenames=filenames,
        cer_thresh=Configs.cer_thresh, 
        device=Configs.device, 
        wada_snr_score_filter=Configs.wada_snr_score_filter
    )
    r.run()


def run_filter(path_pickles, path_bad_cuts, shaffle_files=True):
    """
    Запускает фильтрацию файлов в параллельных процессах.

    :param path_pickles: Путь к директории с файлами pickle
    :param path_bad_cuts: Путь к директории для сохранения отбракованных файлов
    :param shuffle_files: Флаг для случайного перемешивания файлов
    """
    filenames = os.listdir(path_pickles)
    if shaffle_files:
        random.shuffle(filenames)
    mid = len(filenames) // 2
    filenames_part1 = filenames[:mid]
    filenames_part2 = filenames[mid:]
    
    process1 = multiprocessing.Process(target=_run_parallel, args=(path_pickles, path_bad_cuts, filenames_part1))
    process2 = multiprocessing.Process(target=_run_parallel, args=(path_pickles, path_bad_cuts, filenames_part2))
    
    process1.start()
    process2.start()
    
    process1.join()
    process2.join()
    print("Done")


if __name__ == "__main__":
    run_filter(
    Configs.path_pickles,
    Configs.path_bad_cuts,
    )