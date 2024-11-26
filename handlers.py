import logging
from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from services import transcribe_audio
from config import BotConfig

logger = logging.getLogger(__name__)

config = None

async def handle_audio(message: types.Message, state: FSMContext):
    if message.content_type != types.ContentType.AUDIO:
        return

    model = await state.get_state()
    if not model:
        await select_model(message, state)
        return

    logger.info(f"Выбрана модель: {model}")
    try:
        result = await transcribe_audio(message.audio.file_id, model, config.api.deep_foundation_key)
        await message.answer(result.format_markdown())
    except Exception as e:
        logger.exception(f"Ошибка при обработке аудио: {e}")
        await message.answer("Произошла ошибка при обработке аудио. Попробуйте позже.")


async def select_model(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=model, callback_data=model)]  # Add buttons for each model
        for model in config.models
    ])
    await message.answer("Выберите модель:", reply_markup=keyboard)



async def process_callback(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(query.data)
    await query.answer("Модель выбрана")
    await query.message.edit_reply_markup()

def register_handlers(dp: Dispatcher, config_instance: BotConfig):
    global config
    config = config_instance
    dp.message.register(handle_audio)
    dp.message.register(select_model)
    dp.callback_query.register(process_callback)

