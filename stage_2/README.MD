

# Speaker Filter and Speaker extract

Эта часть предназначена для фильтрации датасета. Он включает в себя фильтрацию данных, выделение спикеров из датасета.

### Структура проекта

Проект состоит из нескольких файлов, каждый из которых выполняет свою функцию:


* filter.py - Фильтрация аудиофайлов на основе заданных критериев (например, качество звука (SNR) и CER).

* speakers.py - Определение говорящих и их эмбеддингов на основе аудиофайлов.

* update_files.py - Обновление и сохранение средних эмбеддингов для мужчин и женщин.
Установка зависимостей


### Установка зависимостей
Перед запуском необходимо установить необходимые зависимости.

```sh
pip install -r requirements.txt
```


### Заупск
---
1. Часть фильтрации.

* <b>Необходимо обновть Configs в файле filter.py.</b> Нужно обновить все необходимые поля.

```sh
docker build -t filter_image -f Dockerfile_filter .
docker run -it --mount type=bind,source=/opt/datasets/FINAL_TRANSCRIPTIONS/,target=/DATA/PICKLES/ --mount type=bind,source=/opt/datasets/FINAL_BAD_CUTS/,target=/DATA/BAD_CUTS/ --gpus all filter_image
```
---
2. Часть разделения по спикерам.

* <b>Необходимо обновть Configs в файле speakers.py и update_files.py.</b> Нужно обновить все необходимые поля!
*   speakers.py - создает csv файл с полями (название файла; гендр; speaker_id)
* speakers.py - сохраняет файлы со средним эмбеддингми спикеров для male и female отдельно.
* Обновляет pikle файлы и добавляет все необходимые поля.


```sh
python3 speakers.py
python3 update_files.py
```
---