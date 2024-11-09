# Описание кода

- [Описание кода](#описание-кода)
  - [AudioQuality (enum)](#audioquality-enum)
  - [AudioFileBase (class)](#audiofilebase-class)
  - [AudioFile (class)](#audiofile-class)
  - [AudioFileSegment (class)](#audiofilesegment-class)
  - [download\_youtube (function)](#download_youtube-function)
  - [download\_rutube (function)](#download_rutube-function)
  - [download\_audio\_vk\_video (function)](#download_audio_vk_video-function)
  - [UrlManager (class)](#urlmanager-class)
  - [ffmpeg\_audio\_converter (function)](#ffmpeg_audio_converter-function)
  - [pcm2float (function)](#pcm2float-function)
  - [float2pcm (function)](#float2pcm-function)
  - [DataDownloader (class)](#datadownloader-class)
  - [SourceAdapter (class)](#sourceadapter-class)
  - [process\_pickle\_files (function)](#process_pickle_files-function)
  - [process\_single\_file (function)](#process_single_file-function)
  - [normalize\_russian (function)](#normalize_russian-function)
  - [whisper\_parse (function)](#whisper_parse-function)
  - [segment\_audio\_wisper (function)](#segment_audio_wisper-function)
  - [Transcriber (class)](#transcriber-class)
    - [log\_creation (method)](#log_creation-method)
    - [log\_insertion (method)](#log_insertion-method)
    - [get\_audio\_fragment (method)](#get_audio_fragment-method)
    - [save\_audio\_segments (method)](#save_audio_segments-method)
    - [process\_picke\_audio\_files (method)](#process_picke_audio_files-method)
    - [run (method)](#run-method)
  - [main\_download (script)](#main_download-script)
    - [get\_parser (function)](#get_parser-function)
    - [run\_from\_csv](#run_from_csv)
    - [Использование:](#использование)
  - [main\_transcriber (script)](#main_transcriber-script)
  - [Config  (configuration)](#config--configuration)
  - [Dockerfile\_download (Dockerfile)](#dockerfile_download-dockerfile)
  - [Dockerfile\_transcribe (Dockerfile)](#dockerfile_transcribe-dockerfile)
  - [Примеры файлов  для запуска](#примеры-файлов--для-запуска)


Репозиторий voice_cloning

## AudioQuality (enum)
путь: `src/audio/baseaudiofile.py`

AudioQuality - класс перечисление для хранения оценки качества аудио, где

    HIGH = 1
    MEDIUM = 2
    LOW = 3

## AudioFileBase (class)
путь: `src/audio/baseaudiofile.py`

AudioFileBase -  Базовый класс для хранения информации о аудиофайле. Содержит методы для проверки типов данных.

## AudioFile (class)
путь: `src/audio/audiofile.py`

AudioFile - Данный класс предназначен для хранения аудиофайлов

**Атрибуты:**
```
   audio_path: str // Путь до аудио файла
   URL: str // Ссылка на видео
   quality: Union[AudioQuality, int] // Оценка качества аудио (1-3 или enum AudioQuality), где 1 наилучшее качество.
   name: str // Название видео, аудио и тд
   chanel_name: str // Название канала (для видео)
   auto_text: bool // Субтитры ручные или сгенерированы автоматически (флаг автоматических). True означает, что субтитры сгенерированы автоматически
   text: str // субтитры
   time: float // Длина в сек
```

**Методы:**
```
   save_pikle(self, file_path: str) // Сохраняет данные объекта в pickle.
   def load(self, file_path: str): // Загрузка данных из pickle в текущий объект.
   load_pickle(cls, file_path: str) -> AudioFile // Загрузка данных в новый объект класса.
```

## AudioFileSegment (class)
путь: `src/audio/audio_segment.py`

AudioFileSegment - класс для хранения аудиофайлов вместе с метаданными после транскрибации, содержащий в себе аудио файл в виде numpy массива, текст произнесенный в этом аудио и различные метаданные.    

**Атрибуты:**
```
   audio_path: str // Путь до аудио файла
   URL: str // Ссылка на видео
   quality: Union[AudioQuality, int] // Оценка качества аудио (1-3 или enum AudioQuality), где 1 наилучшее качество.
   name: str // Название видео, аудио и тд
   chanel_name: str // Название канала (для видео)
   auto_text: bool // Субтитры ручные или сгенерированы автоматически (флаг автоматических). True означает, что субтитры сгенерированы автоматически
   text: str // субтитры
   time: float // Длина в сек
```

**Методы:**
```
   save_pikle(self, file_path: str) // Сохраняет данные объекта в pickle.
   def load(self, file_path: str): // Загрузка данных из pickle в текущий объект.
   load_pickle(cls, file_path: str) -> AudioFile // Загрузка данных в новый объект класса.
```

## AudioFileSegment (class)
путь: `src/audio/audio_segment.py`

AudioFileSegment - класс для хранения аудиофайлов вместе с метаданными после транскрибации, содержащий в себе аудио файл в виде numpy массива, текст произнесенный в этом аудио и различные метаданные.    

**Атрибуты:**

```
auidio_name: str               // название исходного аудио (.wav) файла
audio_segmnet_index: int        // индекс сегмента в исходном аудио файле (из которого был получен текущий) сегмент
audio_segment_start: float      // начало сегмента аудио в секундах (смещение от начала исходного аудио)
audio_segment_end: float        // конец сегмента аудио в секундах (смещение от начала исходного аудио)
audio: np.ndarray               // аудио в виде массива numpy
URL: str                        // ссылка на исходное видео 
quality: Union[AudioQuality, int] // оценка качества аудио от 1 до 3 
name: str                       // Название видео, аудио и тд
chanel_name: str                // Название канала (для видео)
auto_text: bool                 // Субтитры ручные или сгенерированы автоматически (флаг автоматических). True означает, что субтитры сгенерированы автоматически, при помощи подели ASR
text: str                       // субтитры
time: float                     // Длина в сек

// Необязательные атрибуты
gender: Optional[str]           // Пол говорящего в сегменте (например, 'male' или 'female'). Поле может быть пустым, если информация недоступна
speaker_id: Optional[int]       // Идентификатор говорящего, если доступен. Поле может отсутствовать
wada_snr_score: Optional[float] // Оценка отношения сигнал/шум по алгоритму WADA-SNR, используется для анализа качества записи. Поле может отсутствовать
old_text_transcription: Optional[str] // Предыдущая версия текстовой транскрипции, если доступна. Поле может отсутствовать
number_of_speakers: Optional[int] // Число говорящих в аудиофайле. Поле может быть пустым, если информация недоступна

```

**Методы:**

```
save_pickle(file_path: str) -> bool // сохраняет данные объекта в файл pickle. При сохранении включаются только те необязательные поля, которые заданы.
    
load(file_path: str) -> None // загружает данные из файла pickle в текущий объект. Если в файле отсутствуют некоторые необязательные поля, они остаются пустыми (None).
    
load_pickle(file_path: str) -> AudioFileSegment // загружает данные из файла pickle в новый объект класса `AudioFileSegment` и возвращает его. Необязательные поля инициализируются как None, если отсутствуют в файле.

dump_wav(save_file_path: str) -> None // аудиоданные сохраняются в виде файла WAV.
    
load_wav(file_path: str) -> None // загружает аудиоданные из файла WAV в `self.array`.

```

## download_youtube (function)
путь: `src/downloaders/youtube_downloader.py`

download_youtube - функция скачивания аудиодорожек из видео по ссылкам на YouTube и сохранение их в указанную директорию.

**Параметры:**

```
    urls: list[str] // Список ссылок на видео с YouTube, которые нужно скачать.
    path: str, optional // Директория для сохранения скачанных аудиофайлов. По умолчанию 'audios/'.
    target_sample_rate: int, optional // Частота дискретизации аудио.
```

**Возвращает:**

output_vals: list[dict] // Список словарей, каждый из которых содержит информацию о скачанном аудиофайле:
- 'filename' (str): Название файла.
- 'audio_path' (str): Путь к сохраненному аудиофайлу.
- 'np_audio' (np.ndarray): Аудиоданные в формате NumPy.
- 'url' (str): Ссылка на исходное видео.
- 'name' (str): Название видео.
- 'chanel_name' (str): Имя автора канала.
- 'time' (int): Длительность видео в секундах.
- 'text' (list[dict] или None): Транскрипт видео, если он доступен (список фрагментов субтитров или None).
- 'auto_text' (str): Тип субтитров ('manually' — ручные, 'generated' — автоматически сгенерированные, 'empty' — отсутствуют).

## download_rutube (function)
путь: `src/downloaders/rutube_downloader.py`

 Функция download_rutube - для скачивания аудио дорожки из видео по ссылке на RuTube и сохранение в указанную директорию.

**Параметры:**
```
    url: str // Ссылка на видео на RuTube.
    output_dir: str // Директория для сохранения скачанного файла.
    rate: int, optional // Частота дискретизации аудио. Если None, используется исходная частота аудиофайла.
    print_stats: bool, optional // Если True, выводится информация о процессе загрузки (по умолчанию: True).
    return_numpy: bool, optional // Если True, возвращает аудиофайл в формате NumPy массива. Если False, возвращает только метаданные (по умолчанию: True).
```

Возвращает:

dict: Словарь с информацией о скачанном аудиофайле:
- 'filename' (str): Название файла.
- 'audio_path' (str): Путь к сохраненному аудиофайлу.
- 'np_audio' (np.ndarray): Аудиоданные в формате NumPy, если `return_numpy=True`.
- 'url' (str): Ссылка на исходное видео.
- 'name' (str): Название видео.
- 'chanel_name' (str): Имя автора.
- 'time' (float): Длительность аудиофайла в секундах.
- 'text' (None): Текст субтитров (не реализовано).
- 'auto_text' (None): Флаг автоматических субтитров (не реализовано).

## download_audio_vk_video (function)
путь: `src/downloaders/vk_parser/parsing_vk.py`

Функция download_audio_vk_video - загружает аудио из видеороликов ВК по их URL-адресам и сохраняет их в указанную директорию.

**Параметры:**
```
urls: Union[str, List[str]] // Строка или список строк, представляющих URL-адреса видео VK, с которых нужно скачать аудио.
download_dir: str // Каталог, в котором будут сохранены аудиофайлы и промежуточные файлы.
verbose: bool // Флаг для вывода подробной информации о процессе загрузки.
target_sample_rate: int, optional // Частота дискретизации аудио. По умолчанию 24000.
```

Возвращает:

output_vals: List[dict] Список словарей, содержащих информацию о скачанных аудиофайлах.

## UrlManager (class)
путь: `src/url_store/url_manager.py`

UrlManager - класс для управления списком урлов с дополнительной информацией.

**Параметры:**

```
file_path (str):  // Путь к файлу для хранения данных.
```

**Атрибуты:**

```
file_path (str):  // Путь к файлу для хранения данных.
df (pd.DataFrame):  // DataFrame для хранения урлов и связанных данных.
```

**Методы:**
```
load_urls(): Загружает данные из файла, если он существует.
save_urls(): Сохраняет данные в файл.
add_urls(urls: List[dict], author: str): Добавляет массив урлов с указанными параметрами и автором.
get_all_urls(): Возвращает DataFrame со всеми урлами и их параметрами.
initialize_from_df(df: pd.DataFrame): Инициализирует объект из переданного DataFrame.
```

  
## ffmpeg_audio_converter (function)
путь: `src/utils/audio_converter.py`

Функция ffmpeg_audio_converter конвертирует аудиофайл с использованием FFmpeg, изменяя частоту дискретизации и формат.

**Параметры:**
```
path (str): Путь к исходному аудиофайлу.
path_to_save (str): Путь для сохранения выходного файла.
final_name (str): Имя выходного файла (без расширения).
sample_rate (int): Частота дискретизации выходного аудио (например, 24000 для 24kHz).
output_format (str): Формат выходного файла (например, 'mp3', 'wav').
```

**Ошибки:**
```
ffmpeg.Error: Если при выполнении команды FFmpeg возникли ошибки.
```

**Возвращает:**
```
None: Результат сохраняется в файл на диске, функция ничего не возвращает.
```

## pcm2float (function)
путь: `src/utils/format_convert.py`

Функция pcm2float - преобразует PCM-сигнал в формат с плавающей запятой, нормализуя значения в диапазоне от -1 до 1.

**Аргументы:**
```
sig (array_like):  // Входной массив с PCM-сигналом. Должен быть целочисленного типа данных (например, int16, int32).
dtype (str or np.dtype, optional):  // Тип данных для выходного сигнала с плавающей запятой. По умолчанию 'float32'. Допустимы типы 'float32', 'float64' и другие типы с плавающей запятой.
```

**Ошибки:**
- TypeError: Выбрасывается, если входной сигнал не является массивом целых чисел.
- TypeError: Выбрасывается, если указанный тип данных результата не является типом с плавающей запятой.

**Возвращает:**
numpy.ndarray: Массив с плавающей запятой, нормализованный в диапазоне от -1 до 1.

**Смотрите также:**

```
float2pcm:  // Функция для обратного преобразования сигнала с плавающей точкой обратно в PCM.
numpy.dtype:  // Используется для обработки типов данных.
```

**Примечания:**
Нормализация сигнала выполняется путем масштабирования значений относительно максимального диапазона значений входного целочисленного типа.

Входной сигнал должен быть целочисленным массивом (например, int16, int32).

## float2pcm (function)
путь: `src/utils/format_convert.py`

Функция float2pcm преобразует сигнал с плавающей точкой, который находится в диапазоне от -1 до 1, обратно в PCM формат.

**Аргументы:**
```
sig (array_like): // Входной массив с сигналом в формате с плавающей точкой.
dtype (str or np.dtype, optional): // Тип данных для выходного PCM сигнала. По умолчанию 'int16'. Возможные значения включают 'int32', 'int16' и другие целочисленные типы.
```

**Ошибки:**
- TypeError: Выбрасывается, если входной сигнал не является массивом с плавающей точкой.
- TypeError: Выбрасывается, если указанный тип данных результата не является целочисленным.

**Возвращает:**
numpy.ndarray: Целочисленный массив данных, масштабированный в диапазоне, определённом типом данных dtype.

**Смотрите также:**
pcm2float: Функция для преобразования PCM-сигнала в формат с плавающей точкой.
numpy.dtype: Используется для обработки типов данных.

**Примечания:**
Значения сигнала, выходящие за пределы диапазона [-1.0, 1.0), будут обрезаны.

Преобразование включает масштабирование и сжатие сигнала в соответствии с целочисленным диапазоном типа данных.

Преобразование не включает добавление шума (дизеринг).

## DataDownloader (class)
путь: `src/data_downloader.py`

Класс DataDownloader - Класс для управления загрузкой аудио и видео данных с различных источников. Поддерживает многопоточность, ведение логов и сохранение данных.

**Инициализация:**
```
audios_folder (str): Папка для сохранения аудиофайлов.
log_file_path (str): Путь к файлу логов.
retry_sleep (float): Интервал повторных попыток загрузки.
max_retries (int): Максимальное количество повторных попыток.
num_workers (int): Количество потоков для загрузки.
```

**Методы:**

- log_creation() - Создает файл логов, если не существует.
- log_insertion(status: str, url: str) - Добавляет запись в лог о результате загрузки.
- job_worker(url: str, source_type: str, quality: int = 1) - Обрабатывает и загружает данные по URL источника. Обеспечивает повторные попытки и логирование результатов.
- run(urls: list, sources: list, quality: list) - Запускает загрузку в многопоточном режиме, распределяя задачи по потокам.

**Зависимости:**
AudioFile, download_youtube, download_audio_vk_video, SourceAdapter: Используются для обработки и загрузки данных.

  
## SourceAdapter (class)
путь: `src/source_adapter.py`

Класс SourceAdapter - Адаптер для вызова загрузчиков с различных платформ (Rutube, YouTube, VK). Позволяет загружать аудио и видео, поддерживая разные форматы данных и частоты дискретизации.

Пример использования:

```py

urls = [   'https://rutube.ru/video/77f41a478a208eacbe4d55956480cbd0/',]

for url in urls:

    print(SourceAdapter.download(url, 'rutube', 'outputs', print_stats=True))

```

Метод download(url, source_type, download_dir, rate=24000, print_stats=True, return_numpy=True) -> dict

Загружает контент с указанного источника (Rutube, YouTube, VK).

**Параметры:**
```
url (str): // URL для загрузки.
source_type (str): // Источник контента ('rutube', 'youtube', 'vk').
download_dir (str): // Директория для сохранения файлов.
rate (int):  // Частота дискретизации аудио (по умолчанию 24000).
print_stats (bool): // Флаг для вывода процесса загрузки (по умолчанию True).
return_numpy (bool): // Возвращать ли данные в формате NumPy (по умолчанию True).
```

**Возвращает:**
dict: Словарь с информацией о загруженном контенте.

**Логика работы:**
- Rutube: Использует rutube_downloader.download_rutube.
- YouTube: Вызывает download_youtube, поддерживает одиночные и множественные URL.
- VK: Использует download_audio_vk_video для загрузки аудио с VK.

**Ошибки:**
- ValueError: Если передан неверный тип источника.

## process_pickle_files (function)
путь: `src/normalization/normalization.py`

process_pickle_files - эта функция обрабатывает файлы pickle, содержащие текстовые данные, нормализует их и сохраняет результат в новый ключ словаря. 

process_pickle_files(pickle_folder, save_folder=None, change_inplace=False, max_workers=10)

Обрабатывает все файлы pickle в указанной папке с помощью многопоточности.

**Параметры:**
```
pickle_folder (str): // Путь к папке с файлами pickle.
save_folder (str, необязательно): // Папка для сохранения обновлённых файлов (если не изменяется на месте).
change_inplace (bool): // Если True, изменения вносятся прямо в исходные файлы. Если False, создаётся новая копия.
max_workers (int):  // Количество потоков для параллельной обработки файлов.
```

**Описание:**
Функция использует ThreadPoolExecutor для параллельной обработки файлов и нормализации текста.

Если изменения вносятся не на месте, проверяется наличие папки для сохранения и при необходимости создаётся новая.

Каждый файл обрабатывается отдельным потоком с использованием функции process_single_file.

## process_single_file (function)
путь: `src/normalization/normalization.py`

process_single_file(pickle_file, save_folder_path=None, change_inplace=False):

Обрабатывает один файл pickle: нормализует текст и сохраняет результат. Добавляется новый ключ в словарь под ключом `normalized_text` если его нет в словаре, иначе файл пропускается.

**Параметры:**
```
pickle_file (Path):  // Путь к файлу pickle.
save_folder_path (Path, необязательно): // Папка для сохранения изменённого файла (если не изменяется на месте).
change_inplace (bool): // Если True, изменения вносятся прямо в исходный файл. Если False, создаётся новая копия.
```

**Возвращает:**
True, если файл успешно обработан, или False, если возникла ошибка.

## normalize_russian (function)
путь: `src/normalization/text_normalizer.py`

Для нормализации текста на русском языке используется код из данного репозитория [https://github.com/shigabeev/russian_tts_normalization](https://github.com/shigabeev/russian_tts_normalization).

Расширение аббревиатур: Преобразует аббревиатуры в их произношение на русском.

Нормализация дат: Преобразует даты в текстовом формате (например, "12.03.2021") в их текстовое представление ("двенадцатое марта две тысячи двадцать первого года").

Нормализация валют: Преобразует суммы в валюте в их текстовые представления (например, "100 рублей" в "сто рублей").

Нормализация телефонных номеров: Преобразует телефонные номера в их словесные формы.

Нормализация чисел: Преобразует числовые значения в их словесные формы.

Транслитерация: Преобразует латинские символы в кириллические с учётом распространённых диграфов.

Функция предназначена для обработки текста с различными числовыми, датированными и сокращёнными элементами, делая его пригодным для текстовых задач, таких как синтез речи (TTS).

Интерфейс нормализации представлен через функцию normalize_russian

```
normalize_russian(text: str) -> str
```

Данная функция выполняет нормализацию русского текста.

## whisper_parse (function)
путь: `src/split_audio/segment_audio.py`

Функция whisper_parse(parsed_json: dict)

Разбирает JSON-объект с результатами распознавания речи, выполненного Whisper, и извлекает предложения с их временными метками начала и конца.

**Аргументы:**
```
parsed_json (dict): // JSON-объект, содержащий сегменты и слова, извлеченные из аудио (результат работы Whisper).
```

**Возвращает:**
list: Список кортежей, где каждый кортеж содержит предложение, время его начала и конца.

  
## segment_audio_wisper (function)
путь: `src/split_audio/segment_audio.py`

Функция segment_audio_wisper(audio_path: str, device='cuda', model_type='small')

Сегментирует аудиофайл на основе модели Whisper, выполняет распознавание речи и возвращает временные метки для каждого сегмента.

**Аргументы:**
```
audio_path (str): // Путь к аудиофайлу для сегментации.
device (str): // Устройство для выполнения модели ('cuda' или 'cpu', по умолчанию 'cuda').
model_type (str): // Тип модели Whisper для использования (доступные варианты: 'tiny', 'small', 'medium').
```

**Возвращает:**
tuple: Кортеж, содержащий путь к аудиофайлу и список сегментов с временными метками.

  
## Transcriber (class)
путь: `src/split_audio/transcriber.py`

Класс Transcriber - класс для транскрибирования и сегментации аудиофайлов с использованием модели Whisper. Поддерживает многопоточную обработку и сохранение сегментов в отдельные файлы.

__init__(save_segments_folder: str, pickles_audio_folder: str, wav_audio_folder: str, log_file_path: str, num_workers: int, device: str = "cuda", model_type: str =  "small") -> None

Инициализирует объект для обработки аудиофайлов.

**Параметры:**
```
save_segments_folder (str): Папка для сохранения сегментов.
pickles_audio_folder (str): Папка с pickle-объектами аудио.
wav_audio_folder (str): Папка с аудиофайлами в формате WAV.
log_file_path (str): Путь к файлу лога.
num_workers (int): Количество рабочих потоков.
device (str): Устройство для инференса модели ('cuda', 'cpu').
model_type (str): Тип модели Whisper ('tiny', 'small', 'medium').
```

**Методы**:

### log_creation (method)
Создает лог-файл с заголовками, если файл не существует.

### log_insertion (method)
 log_insertion(status: str, audio_pickle_name: str) - Вставляет запись в лог-файл о статусе обработки аудиофайла.

**Параметры:**

```
status (str): Статус обработки ("OK" или "ERROR").
audio_pickle_name (str): Название pickle-объекта аудио.
```

### get_audio_fragment (method)

get_audio_fragment(encoded_data, audio, sample_rate)

Извлекает фрагмент аудио на основе временных меток сегмента.

**Параметры:**
```
encoded_data (tuple): // Текст и временные отметки сегмента.
audio (ndarray): // Аудиосигнал.
sample_rate (int): // Частота дискретизации.
```

**Возвращает:**
Кортеж: аудиофрагмент и текст сегмента.

### save_audio_segments (method)
save_audio_segments(audio_file_object, path_to_wav_file, split_restults, save_folder)

Сохраняет сегменты аудио в файлы и сериализует их с помощью pickle.

**Параметры:**
```
audio_file_object (AudioFile): // Объект с метаданными аудиофайла.
path_to_wav_file (str): // Путь к исходному WAV файлу.
split_results (list): // Результаты сегментации аудио.
save_folder (str): // Путь для сохранения сегментов.
```


### process_picke_audio_files (method)
process_picke_audio_files(args):

Обрабатывает pickle-файлы аудио, сегментирует их и сохраняет сегменты.

**Параметры:**
```
args (tuple): // Включает путь к pickle-файлу, флаг удаления WAV-файлов и мьютекс для логирования.
```

### run (method)
run(paths_to_pickle_object: List[str], remove_wav_after_complete=False):

Запускает параллельную обработку нескольких pickle-файлов.

**Параметры:**
```
paths_to_pickle_object (List[str]): // Список путей к pickle-файлам.
remove_wav_after_complete (bool): // Удалять ли WAV-файлы после обработки.
```


## main_download (script)
путь: `main_download.py`

Этот скрипт запускает процесс загрузки аудио- и видеоданных с различных источников на основе CSV-файла с URL-адресами. Использует многопоточную загрузку, логирование и возможность повторных попыток в случае неудачных загрузок.

### get_parser (function)
путь: `main_download.py`

Функция `get_parser()` Создает и возвращает объект ArgumentParser для обработки командной строки.

**Возвращает:**
argparse.ArgumentParser: Парсер аргументов командной строки.

### run_from_csv
путь: `main_download.py`

Функция run_from_csv(csv_path, dataset_path, logging_path, retry_sleep=3, max_retries=3, num_workers=2)

Запускает процесс загрузки на основе URL-адресов из CSV-файла.

**Параметры:**
```
csv_path (str): // Путь к CSV-файлу с URL-адресами.
dataset_path (str): // Путь к папке, в которой будет создан датасет.
logging_path (str): // Путь к файлу логов.
retry_sleep (float): // Время ожидания между попытками загрузки.
max_retries (int): // Максимальное количество попыток загрузки.
num_workers (int): // Количество параллельных потоков.
```

### Использование:
Запуск скрипта осуществляется из командной строки с передачей аргументов:

```bash
python main_download.py --csv-path path_to_csv --dataset-path path_to_dataset --logging-path path_to_log --retry-sleep 3 --max-retries 3 --num-workers 2
```

**Аргументы:**
```
--csv-path: Путь к CSV-файлу с URL-адресами.
--dataset-path: Путь к папке для сохранения данных.
--logging-path: Путь к файлу логов.
--retry-sleep: Время между повторными попытками (по умолчанию 3 секунды).
--max-retries: Максимальное количество попыток (по умолчанию 3).
--num-workers: Количество потоков для параллельной загрузки (по умолчанию 2).
```

## main_transcriber (script)
путь: `main_transcriber.py`

Этот скрипт выполняет автоматическую обработку аудиофайлов, разделяя их на сегменты с помощью класса Transcriber. Он динамически обновляет список файлов для обработки и обрабатывает только новые файлы, указанные в специальном файле с именами.

**Основные шаги:**

**Инициализация Transcriber:**

Создается экземпляр класса Transcriber с параметрами, заданными в конфигурационном файле config. Папка для сохранения сегментов создается, если она еще не существует.

**Сбор списка файлов для обработки:**

Если включена опция автоматического поиска файлов (config.auto_filenames_to_process), скрипт собирает все .pickle файлы из указанной папки и записывает их относительные пути в файл для дальнейшей обработки.

**Основной цикл обработки:**

Скрипт считывает имена файлов из файла и проверяет, появились ли новые файлы по сравнению с последней итерацией. Если новые файлы обнаружены, они передаются на обработку в метод run объекта Transcriber. Если новых файлов нет, обработка завершается.

**Завершение работы:**

По завершении обработки скрипт выводит общее время выполнения.

**Переменные и файлы:**
- config: Модуль с параметрами, задающими пути к папкам, устройствам, количеству потоков и т.д.
- filenames_to_process: Файл, содержащий список путей к файлам .pickle, которые необходимо обработать.
- Transcriber: Класс, отвечающий за сегментацию и сохранение аудиофайлов.

**Основные параметры:**
- save_segments_folder: Путь для сохранения сегментов аудио.
- pickles_audio_folder: Путь к папке с pickle-файлами.
- wav_audio_folder: Путь к папке с WAV-файлами.
- log_file_path: Путь к файлу логов.
- num_workers: Количество потоков для параллельной обработки.
- device: Устройство для обработки (например, 'cuda' для GPU).
- model_type: Тип модели Whisper для транскрибирования.

  
## Config  (configuration)
путь: `config.py`

Этот файл конфигурации содержит пути и настройки для обработки и транскрибирования аудиофайлов с использованием модели Whisper в многопоточном режиме.

**Переменные:**
```
root_path: // Путь до корневой директории репозитория с кодом, динамически определяется с помощью os.getcwd().
cluster_wav_folder: // Путь до папки с WAV-файлами, которые необходимо обработать.
cluster_pickle_folder: // Путь до папки с pickle-файлами, содержащими данные для обработки.
filenames_to_process: // Имя файла, в котором содержатся пути до файлов, подлежащих транскрибированию.
log_filename: // Имя файла для хранения логов о выполненной обработке.
input_path: // Путь до папки, где находятся файл с путями до файлов .pickle (определяемый filenames_to_process) и файл логов обработки.
auto_filenames_to_process: // Флаг, указывающий, нужно ли автоматически создавать файл с именами файлов для обработки (True или False).
segments_folder: // Путь до папки, где будут сохраняться результаты транскрибирования и сегментации аудиофайлов.
num_workers: // Количество параллельных процессов, используемых для обработки.
device: // Устройство для обработки. Возможные значения: 'cpu' или 'cuda' (для использования GPU).
model_type: // Тип модели Whisper, которая будет использоваться для транскрибирования. Возможные значения: 'tiny', 'small', 'medium'.
```


## Dockerfile_download (Dockerfile)
путь: `Dockerfile_download`

Этот Dockerfile создаёт контейнер для запуска скрипта Python, который скачивает аудиофайлы

Перед запуском скрипта необходимо установить логин, пароль, токен для аккаунта в VK в Dockerfile_download (см. doc.md). Также при необходимости измените параметры запуска контейнера в Dockerfile_download docker run. 

**Установка переменных окружения:**
```
ENV API_VK_LOGIN=88124567891
ENV API_VK_PASSWORD=password
ENV API_VK_TOKEN=vk1.a.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Параметры запуска программы:**
```
CMD ["/bin/bash", "-c", "source activate tts_data1 && python3 main_download.py --csv-path test_urls.txt --dataset-path DOWNLOADS/ --logging-path DOWNLOADS/test_logs.txt --num-workers 2"]
```

Для запуска необходимо следующее 

```
docker build -t tts_data_image -f Dockerfile_download .

docker run -it --mount type=bind,source=/opt/datasets/DWL_DATA_1,target=/app/DOWNLOADS/ --gpus all tts_data_image
```

## Dockerfile_transcribe (Dockerfile)
путь: `Dockerfile_transcribe

Этот Dockerfile создаёт контейнер для запуска скрипта, связанного с транскрибированием аудиофайлов с использованием модели Whisper.

Для запуска необходимо следующее 

```
docker build -t tts_data_transcribe -f Dockerfile_transcribe .

docker run -it --mount type=bind,source=/opt/datasets/DWL_DATA_1/,target=/app/DOWNLOADS/ --mount type=bind,source=/opt/datasets/TRANSCRIBED_DATA_1/,target=/app/TRANSCRIPTIONS/ --gpus all tts_data_transcribe
```



## Примеры файлов  для запуска

Пример содержания файла для скачивания аудио:
```
id,url,quality,source,author
1,https://vk.com/video292039158_456240381,1,vk,user1
2,https://vk.com/video292039158_456240380,2,vk,user1
3,https://vk.com/video292039158_456240378,3,vk,user1
4,https://rutube.ru/video/c710e653f26694c0624efa7a8dfa7a41/,2,rutube,user2
5,https://rutube.ru/video/f5192c90bb9669d5a1c05e88b5ad36b5/,3,rutube,user2
```

Пример содержания файла для транскрибации аудио:
```
vk/(Source:VkVideo)video292039158_456240331.pickle
vk/(Source:VkVideo)video292039158_456240333.pickle
vk/(Source:VkVideo)video292039158_456240334.pickle
rutube/(Source:RuTube)(author:Аудиокниги_слушать_онлайн-2548895872464428564)(title:Тимоти_Тэтчер_Ищи_меня_в_-4308454008745122772).pickle
rutube/(Source:RuTube)(author:Аудиокниги_слушать_онлайн-2548895872464428564)(title:Энн_Райс_Скрипка_3-8132078218763678093).pickle
```

