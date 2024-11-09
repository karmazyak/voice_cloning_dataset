import whisper_timestamped as whisper
from whisper.model import disable_sdpa

SHIFT = 0.5
MIN_WORD_IN_SENTENCE = 5
MIN_DURATION = 1.0

def whisper_parse(parsed_json : dict):
    """
    Разбирает переданный JSON-объект и извлекает предложения вместе с их началом и концом.

    Аргументы:
    ----------
    parsed_json (dict): JSON-объект, содержащий разобранные данные аудио.
    Результат работы whisper_timestamped.

    Возвращает:
    -----------
    list: Список кортежей, где каждый кортеж содержит предложение, время его начала и конца.
    """
    result = []
    for seg_index, segment in enumerate(parsed_json['segments']):
        temp_sentence = ''
        if 'words' not in segment:
            continue
        for index_sentence, word in enumerate(segment['words']):
            if temp_sentence == '':
                start_time = word['start']
            temp_sentence += ' ' + word['text'].strip() 
            if temp_sentence[-3:] == '...' or temp_sentence[-1] == '.' or temp_sentence[-1] == '!' or temp_sentence[-1] == '?' or temp_sentence[-1] == '…':
                # Use shift at end of sentence to avoid interruptions in the middle of a word
                if (index_sentence + 1) < len(segment['words']): # is not end of current segment 
                    max_dur = segment['words'][index_sentence + 1]['start']
                else:
                    #next segment
                    try:
                        if (seg_index + 1) < len(parsed_json['segments']):
                            max_dur = parsed_json['segments'][seg_index + 1]['words'][0]['start']
                        else: # curr segment is last
                            max_dur = word['end']
                    except:
                        max_dur = word['end']
                end_time = min((word['end'] + max_dur) / 2, word['end'] + SHIFT)
                temp_sentence = temp_sentence.strip()
                if len(temp_sentence.split()) < MIN_WORD_IN_SENTENCE or (end_time - start_time) < MIN_DURATION:
                    pass
                else:
                    result.append((temp_sentence, start_time, end_time))
                start_time = None
                temp_sentence = ''
        if temp_sentence != '':
            # same as above
            if (index_sentence + 1) < len(segment['words']):
                max_dur = segment['words'][index_sentence + 1]['start']
            else:
                try:
                    if (seg_index + 1) < len(parsed_json['segments']):
                        max_dur = parsed_json['segments'][seg_index + 1]['words'][0]['start']
                    else:
                        max_dur = word['end']
                except:
                    max_dur = word['end']
            end_time = min((word['end'] + max_dur) / 2, word['end'] + SHIFT) 
            temp_sentence = temp_sentence.strip()
            if len(temp_sentence.split()) < MIN_WORD_IN_SENTENCE or (end_time - start_time) < MIN_DURATION:
                pass
            else:
                result.append((temp_sentence + '.', start_time, end_time))
    return result



def segment_audio_wisper(audio_path, device='cuda', model_type='turbo'):
    """
    Сегментирует аудиофайл по указанному пути на отдельные части с использованием модели Whisper.

    Аргументы:
    ----------
    audio_path (str): Путь к аудиофайлу.
    device (str): Устройство для выполнения моделей (по умолчанию 'cuda').
    model_type (str): Тип модели Whisper для использования ('tiny', 'small' или 'medium', 'turbo').

    Возвращает:
    -----------
    tuple: Кортеж, содержащий путь к аудиофайлу и разобранные данные.
    """
    audio_whisper = whisper.load_audio(audio_path)

    if model_type == "tiny":
        model = whisper.load_model("tiny", device=device)
    elif model_type == "small":
        model = whisper.load_model("lorenzoncina/whisper-small-ru", device=device)
    elif model_type == "medium":
        model = whisper.load_model("lorenzoncina/whisper-medium-ru", device=device)
    elif model_type == "turbo":
        model = whisper.load_model("turbo", device=device)
    else:
        raise ValueError(f"model_type should be 'tiny', 'small' or 'medium', 'turbo'")

    with disable_sdpa():
        transcribed = whisper.transcribe(model,
                        audio_whisper,
                        language="ru",
                        vad="auditok",
                        detect_disfluencies=True,
                        beam_size=5,
                        fp16=True,
                        best_of=5,
                        temperature = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
        )

    
    return (audio_path, whisper_parse(transcribed))
