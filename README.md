# voice_cloning

## Getting started

## Installation
```sh
git clone https://gitlab.di-me.ru/joi/datasets/voice_cloning.git
```


## Использования модуля скачивания источников

Перед запуском скрипта необходимо установить логин, пароль, токен для аккаунта в VK в Dockerfile_download (см. doc.md). Также при необходимости измените параметры запуска контейнера в Dockerfile_download docker run. 
```sh
docker build -t tts_data_image -f Dockerfile_download .
docker run -it --mount type=bind,source=/opt/datasets/DWL_DATA_1,target=/app/DOWNLOADS/ --gpus all tts_data_image
```

## Использование модуля транскрибации текста 
Необходимо именить параметры запуска транскрибации в config.py
Также при необходимости измените парамертры запуска котейнера в Dockerfile_transcribe и docker run. 
```sh
docker build -t tts_data_transcribe -f Dockerfile_transcribe .
docker run -it --mount type=bind,source=/opt/datasets/DWL_DATA_1/,target=/app/DOWNLOADS/ --mount type=bind,source=/opt/datasets/TRANSCRIBED_DATA_1/,target=/app/TRANSCRIPTIONS/ --gpus all tts_data_transcribe


```

## Описание кода
[живёт тут](./contents_description.md)