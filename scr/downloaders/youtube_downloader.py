import os
from audio2numpy import open_audio
from pytube import YouTube
from scr.utils.audio_converters import ffmpeg_audio_converter
from youtube_transcript_api import YouTubeTranscriptApi


def download_youtube(urls: list, path: str = 'audios/', target_sample_rate=24_000) -> list[dict]:
    """
    Скачивание аудиодорожек из видео по ссылкам на YouTube
    и сохранение их в указанную директорию.

    Параметры:
    ----------
    urls: list[str]
        Список ссылок на видео с YouTube, которые нужно скачать.
    path: str, optional
        Директория для сохранения скачанных аудиофайлов. По умолчанию 'audios/'.
    target_sample_rate: int, optional
            Частота дискретизации аудио.
    Возвращает:
    -----------
    output_vals: list[dict]
        Список словарей, каждый из которых содержит информацию о скачанном аудиофайле:
        - 'filename' (str): Название файла.
        - 'audio_path' (str): Путь к сохраненному аудиофайлу.
        - 'np_audio' (np.ndarray): Аудиоданные в формате NumPy.
        - 'url' (str): Ссылка на исходное видео.
        - 'name' (str): Название видео.
        - 'chanel_name' (str): Имя автора канала.
        - 'time' (int): Длительность видео в секундах.
        - 'text' (list[dict] или None): Транскрипт видео, если он доступен (список фрагментов субтитров или None).
        - 'auto_text' (str): Тип субтитров ('manually' — ручные, 'generated' — автоматически сгенерированные, 'empty' — отсутствуют).
    """
    output_vals = []
    for url in urls:
        yt = YouTube(url)
        title = yt.title
        autor = yt.author
        length = yt.length

        autor_save = autor[:25] + str(hash(autor))
        title_save = title[:25] + str(hash(title))
        final_file_name = f'(Source:Youtube)(author:{autor_save})(title:{title_save})'.replace(' ', '_')
        audio_stream = yt.streams.get_audio_only()
        temp_path = audio_stream.download(path)
        ffmpeg_audio_converter(temp_path, path, final_file_name, target_sample_rate, 'wav')
        os.remove(temp_path)

        audio_file_path = f'{path}{final_file_name}.wav'
        np_audio, sr = open_audio(audio_file_path)

        video_id = url.split('?v=')[-1]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        if 'ru' in transcript_list.__dict__['_manually_created_transcripts']:
            transcription = transcript_list.find_manually_created_transcript(['ru']).fetch()
            type_tr = 'manually'
        elif 'ru' in transcript_list.__dict__['_generated_transcripts']:
            transcription = transcript_list.find_generated_transcript(['ru']).fetch()
            type_tr = 'generated'
        else:
            transcription = None
            type_tr = 'empty'

        temp_dict = {
            'filename': final_file_name,
            'audio_path': audio_file_path,
            'np_audio': np_audio,
            'url': url,
            'name': title,
            'chanel_name': autor,
            'time': length,
            'text': transcription,
            'auto_text': type_tr,
        }
        output_vals.append(temp_dict)

    return output_vals


if __name__ == '__main__':
    pass
