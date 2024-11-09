import time
import config
import sys
import os
import time

from pathlib import Path
sys.path.append(config.root_path)
from scr.split_audio.transcriber import Transcriber


os.makedirs(config.segments_folder, exist_ok=True)

transcriber = Transcriber(
    save_segments_folder = config.segments_folder,
    pickles_audio_folder = config.cluster_pickle_folder,
    wav_audio_folder = config.cluster_wav_folder,
    log_file_path = os.path.join(config.input_path, config.log_filename),
    num_workers=config.num_workers,
    device = config.device,
    model_type = config.model_type
)

if config.auto_filenames_to_process:
# Список файлов для обработки
    filenames_to_process = []
    base_path = Path(config.cluster_pickle_folder)

    # Собираем все пути к файлам .pickle
    for file_path in base_path.rglob('*'):
        if file_path.is_file() and file_path.suffix == '.pickle':
            # Append the relative path to filenames_to_process
            filenames_to_process.append(file_path.relative_to(base_path))

     # Записываем относительные пути в файл
    with open(os.path.join(config.input_path, config.filenames_to_process), "w") as file:
        for filename in filenames_to_process:
            file.write(str(filename) + '\n')

last_filenames_len = 0
time_start = time.time()

while(True):
    # Читаем имена файлов из файла
    with open(os.path.join(config.input_path, config.filenames_to_process), 'r') as file:
        filenames = file.read().splitlines()
    filenames_len = len(filenames)
    if(filenames_len == last_filenames_len):
        print('Nothing to process')
        break

    # Обрабатываем новые файлы
    print(filenames)
    transcriber.run(filenames[last_filenames_len:], remove_wav_after_complete=False)
    last_filenames_len = filenames_len

print(f'Total time is {time.time() - time_start}')
print('Done')
