import logging
from aiogram import Dispatcher, types, Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.fsm.context import FSMContext
from services import transcribe_audio
from config import BotConfig
import tempfile
import os
from aiogram.types import FSInputFile

logger = logging.getLogger(__name__)

config = None

bot = Bot(token=os.getenv("TELEGRAM_API_TOKEN"))


async def handle_audio(message: types.Message, state: FSMContext):
    if message.content_type != types.ContentType.AUDIO:
        return

    model = await state.get_state() or config.models[0] # Use default if no model selected

    logger.info(f"Выбрана модель: {model}")
    try:
        result = await transcribe_audio(message.audio.file_id, model, config.api.deep_foundation_key)
        await message.answer(result.format_markdown())

        my_file = open("TextFile.txt", "w+")
        my_file.write(result.text)
        my_file.close()

        await bot.send_document(message.chat.id, FSInputFile("./TextFile.txt"))


    except Exception as e:
        logger.exception(f"Ошибка при обработке аудио: {e}")
        await message.answer("Произошла ошибка при обработке аудио. Попробуйте позже.")


async def select_model(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=model) for model in config.models]
    ], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите модель (или отправьте аудио для использования модели по умолчанию):", reply_markup=keyboard)
    await state.set_state(None)


async def process_text(message: types.Message, state: FSMContext):
    await state.set_state(message.text)
    await message.answer("Модель выбрана")


def register_handlers(dp: Dispatcher, config_instance: BotConfig):
    global config
    config = config_instance
    dp.message.register(handle_audio)
    dp.message.register(select_model)
    dp.message.register(process_text)

