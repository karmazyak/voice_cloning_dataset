import os 
# Общие параметры данных
#=======================================================================================
root_path = os.getcwd() # Путь до репозитория с кодом
cluster_wav_folder = '/app/DOWNLOADS/audio' # Путь до папки с вавками
cluster_pickle_folder = '/app/DOWNLOADS/pickles' # Путь до папки с пиклами
filenames_to_process = 'input_transcribe_test.txt' # Файл с названиями файлов для транскрибации 
log_filename = 'processed_1.csv' # Назавание файлами с логами транскрибации
input_path = '/app/DOWNLOADS' # Путь до папки, где лежит файл с путями до .pickle файлов (filenames_to_process) и processed.txt с логами обработки
auto_filenames_to_process = False # Флаг указывающй необходимо ли создавать {filenames_to_process} (файл с путями до .pickle файлов) автоматически
segments_folder = '/app/TRANSCRIPTIONS/' # Путь до папки, где будут сохраняться файлы с транскрибацией.
num_workers = 2 # Кол-ва параллельных прлцессов
device = 'cuda' # Устройство
model_type = 'turbo' # Тип модели Whisper
#========================================================================================