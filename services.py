import os
import logging
import aiohttp
from aiogram.types import Audio
from dataclasses import dataclass
import re
import time
from aiogram import Bot
from dotenv import load_dotenv
import tempfile

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_API_TOKEN"))

logger = logging.getLogger(__name__)

@dataclass
class TranscriptionResult:
    text: str
    input_length_ms: int
    transcription_time: float
    audio_size_bytes: int
    tokens_used: int

    def format_markdown(self) -> str:
        """Форматирует результат в Markdown с выделением числовых значений."""
        text = f"""
Транскрипция:
{self.text}

Результаты:
• Длительность аудио: {self.input_length_ms / 1000:.2f} сек
• Время транскрипции: {self.transcription_time:.2f} сек
• Размер аудио: {self.audio_size_bytes / (1024 * 1024):.2f} МБ
• Токенов использовано: {self.tokens_used}

"""
        return text


async def transcribe_audio(file_id: str, model: str, api_key: str) -> TranscriptionResult:
    """Транскрибирует аудиофайл с помощью Deep Foundation API."""
    try:
        logger.info(f"Начало транскрипции с моделью {model}")
        start_time = time.time()
        file = await get_file(file_id)
        if file is None:
            raise Exception("Не удалось получить файл.")

        async with aiohttp.ClientSession() as session:
            with open(file.name, "rb") as audio_file:
                form = aiohttp.FormData()
                form.add_field('file', audio_file, filename=os.path.basename(file.name))
                form.add_field('model', model)
                form.add_field('language', 'RU')

                async with session.post(
                    "https://api.deep-foundation.tech/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    data=form
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info("Успешная транскрипция.")
                        return TranscriptionResult(
                            text=response_data.get("text", "Транскрипция не удалась."),
                            input_length_ms=response_data.get('input_length_ms', 0),
                            transcription_time=time.time() - start_time,
                            audio_size_bytes=os.path.getsize(file.name),
                            tokens_used=response_data.get('input_length_ms', 0)
                        )
                    else:
                        logger.error(f"Ошибка API Deep Foundation: {response.status} - {await response.text()}")
                        raise Exception(f"Ошибка API Deep Foundation: {response.status}")
    except Exception as e:
        logger.exception(f"Ошибка транскрипции: {e}")
        raise


async def get_file(file_id: str) -> tempfile.NamedTemporaryFile or None:
    """Загружает аудиофайл из Telegram и возвращает временный файл."""
    try:
        file = await bot.get_file(file_id)
        if file is None:
            return None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            file_path = temp_file.name
            await bot.download_file(file.file_path, file_path)
        return temp_file
    except Exception as e:
      logger.exception(f"Ошибка при получении файла: {e}")
      return None