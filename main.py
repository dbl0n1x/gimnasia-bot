import asyncio
import os
import webbrowser
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import InputFile, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from large_messages import *
from vk_api_json import get_images

API_TOKEN = "8241773401:AAEpZwq2CIECAH69AgheN4BikCMwBtbAKUw"
bot = Bot(API_TOKEN)
dp = Dispatcher()

TMP_PATH = "tmp"
Path(TMP_PATH).mkdir(parents=True, exist_ok=True)
UPDATE_INTERVAL = 6 * 60 * 60  # 6 часов

# -------------------------------
#      Автообновление фото
# -------------------------------
async def auto_update():
    while True:
        try:
            updated = get_images(update=True)
            if updated:
                print("📢 Автообновление: новые фото загружены!")
            else:
                print("ℹ️ Автообновление: новых фото нет.")
        except Exception as e:
            print("❌ Ошибка при автообновлении:", e)
        await asyncio.sleep(UPDATE_INTERVAL)


# -------------------------------
#             Команды
# -------------------------------
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer(welcome_message, parse_mode="HTML")


@dp.message(F.text == "/teachers")
async def cmd_teachers(message: types.Message):
    await message.answer(teachers_message, parse_mode="HTML")


@dp.message(F.text == "/probnick")
async def cmd_probnick(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Нажми", url="https://fipi.ru/")]]
    )
    await message.answer(
        "Лучший сборник пробников чтобы подготовиться к ОГЭ📚(fipi)",
        reply_markup=kb
    )
    webbrowser.open("https://fipi.ru/")


@dp.message(F.text == "/oge")
async def cmd_oge(message: types.Message):
    await message.answer(oge_message, parse_mode="HTML")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text="Нажми",
            url="https://4ege.ru/gia-in-9/76918-raspisanie-oge-2026.html"
        )]]
    )

    await message.answer("Либо можешь перепроверить здесь", reply_markup=kb)


@dp.message(F.text == "/interview")
async def cmd_interview(message: types.Message):
    await message.answer(interview_message, parse_mode="HTML")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text="Нажми",
            url="https://4ege.ru/gia-po-russkomu-jazyku/76235-daty-provedenija-itogovogo-sobesedovanija-2026.html"
        )]]
    )

    await message.answer("Либо можешь перепроверить здесь", reply_markup=kb)


# -------------------------------
#   Функция рассылки (пустышка)
# -------------------------------
def subscribe_a_mailing():
    print("Функция вызвана!")


# -------------------------------
#          /schedule
# -------------------------------
@dp.message(F.text == "/schedule")
async def cmd_schedule(message: types.Message):
    image_files = [f for f in os.listdir(TMP_PATH) if f.lower().endswith(".jpg")]

    # Если нет изображений → пытаемся загрузить
    if not image_files:
        get_images()
        image_files = [f for f in os.listdir(TMP_PATH) if f.lower().endswith(".jpg")]

    if not image_files:
        await message.answer("Изображения не найдены 😕")
        return

    media = []
    for filename in image_files:
        file_path = os.path.join(TMP_PATH, filename)
        media.append(InputMediaPhoto(media=InputFile(file_path)))

    await bot.send_media_group(message.chat.id, media)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="call_func")],
            [InlineKeyboardButton(text="Нет", callback_data="call_func")],
        ]
    )

    await message.answer(schedule_message, reply_markup=kb)


# -------------------------------
#        /materials
# -------------------------------
@dp.message(F.text == "/materials")
async def cmd_materials(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Русский язык", callback_data="call_func")],
            [InlineKeyboardButton(text="Математика", callback_data="call_func")],
        ]
    )
    await message.answer(
        "Выберите по какому предмету вы хотите получить справочный материал:",
        reply_markup=kb
    )


@dp.message(F.text == "/help")
async def cmd_help(message: types.Message):
    await message.answer(help_text)


@dp.message(F.text == "/update")
async def cmd_update(message: types.Message):
    await message.answer("🔄 Проверяю обновления...")
    updated = get_images(update=True)

    if updated:
        await message.answer("✅ Есть новые расписания! Используй /schedule")
    else:
        await message.answer("ℹ️ Новых расписаний нет.")


# -------------------------------
#    Callback handler
# -------------------------------
@dp.callback_query(F.data == "call_func")
async def callback_handler(callback: types.CallbackQuery):
    subscribe_a_mailing()
    await callback.answer("Функция вызвана!")


# -------------------------------
#            Запуск
# -------------------------------
async def main():
    # Запуск фоновой задачи автообновления
    asyncio.create_task(auto_update())

    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


