import torchaudio
import torch
import numpy as np
import torch.nn.functional as F

from typing import List, Optional, Union, Dict, Literal

from transformers import (
    AutoFeatureExtractor,
    AutoModelForAudioClassification,
    Wav2Vec2Processor
)

class CollateFunc:
    """Функция для предварительной обработки аудиоданных перед классификацией."""
    def __init__(
        self,
        processor: Wav2Vec2Processor,
        padding: Union[bool, str] = True,
        pad_to_multiple_of: Optional[int] = None,
        return_attention_mask: bool = True,
        sampling_rate: int = 16000,
        max_length: Optional[int] = None,
    ):
        self.sampling_rate = sampling_rate
        self.processor = processor
        self.padding = padding
        self.pad_to_multiple_of = pad_to_multiple_of
        self.return_attention_mask = return_attention_mask
        self.max_length = max_length
 
    def __call__(self, batch: List[Dict[str, np.ndarray]]):
        """
        Обрабатывает пакет данных для подачи в модель.

        :param batch: Список словарей с аудиоданными
        :return: Словарь с обработанными значениями
        """
        input_values = [item["input_values"] for item in batch]
        batch = self.processor(
            input_values,
            sampling_rate=self.sampling_rate,
            return_tensors="pt",
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_attention_mask=self.return_attention_mask
        )
        return {
            "input_values": batch.input_values,
            "attention_mask": batch.attention_mask if self.return_attention_mask else None
        }

class GenderRecognition():
    """Класс для распознавания пола говорящего на основе аудиоданных."""
    def __init__(
        self,
        sampling_rate: int = 16000,  
        max_audio_len: int = 5,  
        orig_sr: int = 24000,
        device: str = "cuda"

    ):
        self.model_name_or_path = (
            "alefiury/wav2vec2-large-xlsr-53-gender-recognition-librispeech"
        )
        self.device = torch.device(device)
        self.label2id = {
            "female": 0,
            "male": 1
        }
        self.id2label = {
            0: "female",
            1: "male"
        }
        self.num_labels = 2
        self.sampling_rate = sampling_rate
        self.max_audio_len = max_audio_len
        self.orig_sr = orig_sr
        self.model = AutoModelForAudioClassification.from_pretrained(
            pretrained_model_name_or_path=self.model_name_or_path,
            num_labels=self.num_labels,
            label2id=self.label2id,
            id2label=self.id2label,
        )
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(
            self.model_name_or_path
        )
        self.collator = CollateFunc(
            processor=self.feature_extractor,
            padding=True,
            sampling_rate=sampling_rate,
        )
        self.model.to(self.device)
        self.model.eval()
    
    def convert_audio(self, speech_array):
        """
        Преобразует аудиосигнал для подачи в модель.

        :param speech_array: Массив аудиосигнала
        :return: Словарь с аудиоданными в нужном формате
        """
        if np.issubdtype(speech_array.dtype, np.integer): 
            speech_array = np.array(speech_array, dtype=float) / 32768.0
            
        speech_array = torch.tensor(speech_array, dtype=torch.float32).T
        sr = self.orig_sr
 
        if speech_array.shape[0] > 1:
            speech_array = torch.mean(speech_array, dim=0, keepdim=True)
 
        if sr != self.sampling_rate:
            transform = torchaudio.transforms.Resample(sr, self.sampling_rate)
            speech_array = transform(speech_array)
            sr = self.sampling_rate
 
        len_audio = speech_array.shape[1]
 
        # Pad or truncate the audio to match the desired length
        if len_audio < self.max_audio_len * self.sampling_rate:
            # Pad the audio if it's shorter than the desired length
            padding = torch.zeros(1, self.max_audio_len * self.sampling_rate - len_audio)
            speech_array = torch.cat([speech_array, padding], dim=1)
        else:
            # Truncate the audio if it's longer than the desired length
            speech_array = speech_array[:, :self.max_audio_len * self.sampling_rate]
 
        speech_array = speech_array.squeeze().numpy()
        return {"input_values": speech_array, "attention_mask": None}

    def get_gender(self, class_id: int) -> Literal["female ", "male"]:
        """
        Возвращает строковое значение пола по идентификатору класса.

        :param class_id: Идентификатор класса (0 или 1)
        :return: Пол как строка ("female" или "male")
        """
        return self.id2label[class_id]
        
    @torch.no_grad
    def predict(self, audio: np.array) -> Literal["female ", "male"]:
        """
        Прогнозирует пол говорящего по аудиосигналу.

        :param audio: Аудиосигнал в формате numpy массива
        :return: Пол говорящего ("female" или "male")
        """
        batch = self.convert_audio(audio)
        batch = self.collator([batch])
        input_values, attention_mask = batch['input_values'].to(self.device), batch['attention_mask'].to(self.device)
        logits = self.model(input_values, attention_mask=attention_mask).logits
        scores = F.softmax(logits, dim=-1)
        pred = torch.argmax(scores, dim=1).cpu().detach().numpy()
 
        return self.get_gender(pred[0])
