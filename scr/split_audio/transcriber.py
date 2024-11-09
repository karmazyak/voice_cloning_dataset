import os
import sys
import threading
import traceback
import torch
import librosa
import torchaudio
import multiprocessing
import whisper_timestamped as whisper


from multiprocessing import Pool
from typing import List
from os.path import isfile, basename
from pathlib import Path
from scipy.io import wavfile
from scr.audio import AudioFile, AudioFileSegment
from concurrent.futures import ProcessPoolExecutor
from scr.split_audio.segment_audio import segment_audio_wisper
TORCH_THREADS = 4

class Transcriber():
    """
    Класс для транскрибирования и сегментации аудиофайлов с помощью модели Whisper и сохранения
    сегментов в отдельные файлы.
    """
    def __init__(self,
                save_segments_folder: str,
                pickles_audio_folder: str,
                wav_audio_folder: str,
                log_file_path: str,
                num_workers: int,
                device: str = "cuda",
                model_type: str =  "turbo",
                ) -> None:
        """
        Инициализация объекта Transcriber.

        Args:
            save_segments_folder (str): Путь к папке для сохранения сегментов аудио.
            pickles_audio_folder (str): Путь к папке с сериализованными (pickle) объектами аудио.
            wav_audio_folder (str): Путь к папке с аудиофайлами в формате WAV.
            log_file_path (str): Путь к файлу лога для записи результатов обработки.
            num_workers (int): Количество рабочих потоков для параллельной обработки.
            device (str): Устройство для инференса модели Whisper ('cpu' или 'cuda'). По умолчанию "cuda".
            model_type (str): Тип модели Whisper ('tiny', 'small', 'medium', 'turbo'). По умолчанию "turbo".

        Raises:
            ValueError: Если указаны некорректные пути к директориям или неверное устройство/тип модели.
        """
            
        # Проверка корректности входных данных
        for folder in [save_segments_folder, pickles_audio_folder, wav_audio_folder]:
            if not os.path.isdir(folder):
                raise ValueError(f"{folder} is not a directory")
            
        # Нормализация путей
        self.save_segments_folder = os.path.join(save_segments_folder, '')
        self.pickles_audio_folder = os.path.join(pickles_audio_folder, '')
        self.wav_audio_folder = os.path.join(wav_audio_folder, '')
        
        self.log_file_path = log_file_path
        self.num_workers = num_workers

        if device in {"cuda", "cpu"} or device.startswith("cuda:"):
            self.device = device            
        else:
            raise ValueError(f"{device} should be 'cpu' or 'cuda'")
        
        if model_type not in {"tiny", "small", "medium", "turbo"}:
            raise ValueError(f"{model_type} should one of {'tiny', 'small', 'medium', 'turbo'} ")
        self.model_type = model_type

        # Создание лог-файла, если он не существует
        if not os.path.exists(self.log_file_path):
            self.log_creation()

    def log_creation(self) -> None:
        """
        Создает лог-файл, если он не существует.
        Лог-файл будет содержать три столбца: номер записи, название pickle-объекта и статус обработки.
        """
        with open(self.log_file_path, 'w') as f:
            message = f'number, picle_object, status\n'
            f.write(message)


    def log_insertion(self, status: str, audio_pickle_name: str) -> None:
        """
        Вставляет новую запись в лог-файл.

        Args:
            status (str): Статус обработки ("OK" или "ERROR").
            audio_pickle_name (str): Название pickle-объекта аудиофайла.
        
        Returns:
            None
        """
        with open(self.log_file_path) as f:
            for line in f:
                pass
        max_value = line.split(',')[0]
        if max_value == 'number':
            max_value = 0
        max_value = int(max_value) + 1
        with open(self.log_file_path, 'a') as f:
            message = f'{max_value}, {audio_pickle_name}, {status}\n'
            f.write(message)


    def get_audio_fragment(self, encoded_data, audio, sample_rate):
        """
        Извлекает аудиофрагмент на основе временных отметок и переданного аудиосигнала.

        Args:
            encoded_data (tuple): Кортеж, содержащий текст, начальное и конечное время сегмента.
            audio (ndarray): Аудиосигнал в виде numpy массива.
            sample_rate (int): Частота дискретизации аудиосигнала.

        Returns:
            tuple: Возвращает аудиофрагмент (numpy массив) и текстовую расшифровку сегмента.
        """
        text, start, end = encoded_data
        start_frame, end_frame = int(start * sample_rate), int(end * sample_rate)
        
        # For both mono and multi-channel audios
        if audio.ndim > 1:  # Multi-channel audio
            audio_frame = audio[:, start_frame:end_frame]
        else:  # Mono audio
            audio_frame = audio[start_frame:end_frame]
            
        #Transpose audio
        audio_frame = (audio_frame.T)
        return audio_frame, text


    def save_audio_segments(self, audio_file_object, path_to_wav_file, split_restults, save_folder):
        """
        Сохраняет аудиосегменты в отдельные WAV-файлы и сериализует их с помощью pickle.

        Args:
            audio_file_object (AudioFile): Объект AudioFile, содержащий метаданные аудиофайла.
            path_to_wav_file (str): Путь к исходному аудиофайлу WAV.
            split_results (list): Список сегментов аудио с временными отметками и текстом.
            save_folder (str): Путь к папке для сохранения сегментов.

        Raises:
            ValueError: Если файл не в формате WAV или частота дискретизации не равна 24,000.
        
        Returns:
            None
    """
        if not path_to_wav_file.endswith(".wav"):
            raise ValueError("File must be in WAV format")
        
        if save_folder is None:
            raise ValueError(f"save_folder is None")
        
        if not os.path.isdir(save_folder):
            Path(save_folder).mkdir(parents=True, exist_ok=True)

        sr = librosa.get_samplerate(path_to_wav_file)
        if sr != 24_000:
            raise ValueError(f"Sample rate is {sr}. Expected 24_000")
        
        audio, sr = torchaudio.load(path_to_wav_file, normalize=False)
        audio = audio.numpy()
        file_name = Path(path_to_wav_file).stem
        
        for index, encoded_data in enumerate(split_restults):
            save_file_name = f"{save_folder}/{file_name}_{index}.wav"
            audio_frame, text = self.get_audio_fragment(
                encoded_data=encoded_data,
                audio=audio,
                sample_rate=sr,
                )

            audio_object = AudioFileSegment(
                auidio_name=basename(path_to_wav_file),
                audio_segmnet_index=index,
                audio_segment_start=encoded_data[1],
                audio_segment_end=encoded_data[2],
                audio=audio_frame,
                URL=audio_file_object.URL,
                quality=audio_file_object.quality,
                name=audio_file_object.name,
                chanel_name=audio_file_object.chanel_name,
                auto_text=False,
                text=text,
                time=audio_frame.shape[0] / sr,
                )
            audio_object.save_pickle(save_file_name[:-4] + ".pickle")


    def process_picke_audio_files(self, args):
        """
        Обрабатывает pickle файлы аудио, сегментирует аудиофайлы и сохраняет сегменты.

        Args:
            args (tuple): Кортеж, содержащий:
                - path_to_pickle_object (str): Путь к pickle файлу с объектом AudioFile.
                - remove_wav_after_complete (bool): Флаг для удаления WAV файла после обработки.
                - lock_ (Lock): Мьютекс для синхронизации записи в лог-файл.

        Raises:
            FileNotFoundError: Если pickle файл или соответствующий WAV файл не найден.
            ValueError: Если путь к pickle файлу имеет неверный формат.
        
        """
        path_to_pickle_object, remove_wav_after_complete, lock__ = args[0], args[1], args[2]
        print(f'Starting to process file {path_to_pickle_object}')
        try:
            source_folder = next(
                (folder for folder in ['vk/', 'rutube/', 'youtube/'] if path_to_pickle_object.startswith(folder)), None)
            if not source_folder:
                raise ValueError(f'Unknown source folder')

            concat_path_to_pickle_object = self.pickles_audio_folder + path_to_pickle_object
            if not isfile(concat_path_to_pickle_object):
                raise FileNotFoundError(f'Pickle file {concat_path_to_pickle_object} not found')

            audio_files_object = AudioFile.load_pickle(concat_path_to_pickle_object)
            path_to_wav_file =  self.wav_audio_folder + source_folder + basename(audio_files_object.audio_path)

            if not isfile(path_to_wav_file):
                raise FileNotFoundError(f'Wav file {path_to_wav_file} for pickle not found')

            parsing_results = segment_audio_wisper(path_to_wav_file, self.device, self.model_type)[1]

            self.save_audio_segments(audio_files_object, path_to_wav_file, parsing_results, self.save_segments_folder)
            
            
            with lock__:
                self.log_insertion(status='OK', audio_pickle_name=path_to_pickle_object)
                if(remove_wav_after_complete):
                    os.remove(path_to_wav_file)
                    os.remove(concat_path_to_pickle_object)

            print(f'Pickle object {path_to_pickle_object} processed successfully')
        except Exception as e:
            with lock__:
                self.log_insertion(status='ERROR', audio_pickle_name=path_to_pickle_object)
            print(f'Error while segmenting in pickle object {path_to_pickle_object}: {e}')
            print(f"An error occurred: {e}")
            print(traceback.format_exc())
            print(
                type(e).__name__,          # TypeError
                __file__,                  # ErrorFileName
                e.__traceback__.tb_lineno  # ErrorLine
            )

        return None


    def run(self, paths_to_pickle_object: List[str], remove_wav_after_complete=False):
        """
        Выполняет параллельную обработку нескольких файлов pickle с аудио данными.

        Args:
            paths_to_pickle_object (List[str]): Список путей к pickle файлам для обработки.
            remove_wav_after_complete (bool): Удалять ли WAV файлы после завершения обработки.

        Returns:
            None
        """
        torch.set_num_threads(TORCH_THREADS)
        lock = multiprocessing.Manager().Lock()
        args = [(paths_to_pickle_object[i], remove_wav_after_complete, lock) for i in range(len(paths_to_pickle_object))]
        
        with ProcessPoolExecutor(self.num_workers) as executor:
            try:
                results = executor.map(self.process_picke_audio_files, args)
                for result in results:
                    pass  # Проверяем, возникли ли исключения
            except Exception as e:
                print(f"An error occurred: {e}")
                print(traceback.format_exc())
                print(
                    type(e).__name__,          # TypeError
                    __file__,                  # ErrorFileName
                    e.__traceback__.tb_lineno  # ErrorLine
                )


