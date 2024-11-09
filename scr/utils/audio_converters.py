import ffmpeg


def ffmpeg_audio_converter(path: str, path_to_save: str, final_name: str, sample_rate: int, output_format: str):
    """
    Конвертирует аудиофайл с использованием FFmpeg, изменяя частоту дискретизации и формат.

    Args:
        path (str): Путь к исходному аудиофайлу.
        path_to_save (str): Путь для сохранения выходного файла.
        final_name (str): Имя выходного файла (без расширения).
        sample_rate (int): Частота дискретизации выходного аудио (например, 24000 для 24kHz).
        output_format (str): Формат выходного файла (например, 'mp3', 'wav').

    Raises:
        ffmpeg.Error: Если при выполнении команды FFmpeg возникли ошибки.

    Returns:
        None: Результат сохраняется в файл на диске, функция ничего не возвращает.
    """
    stream = ffmpeg.input(path)
    audio = stream.audio
    output_name = f'{path_to_save}{final_name}.{output_format}'
    stream = ffmpeg.output(audio, output_name, loglevel="quiet", **{'ar': f'{sample_rate}'})
    ffmpeg.run(stream, overwrite_output=True)
