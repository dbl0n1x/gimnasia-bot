import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from vk_api_json import get_images
from large_messages import *
import webbrowser
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

db = sqlite3.connect('users.db')
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS mailing_list (
               user_id  PRIMARY KEY
)""")

db.commit()
db.close()

TMP_PATH = "tmp"
UPDATE_INTERVAL = 6 * 60 * 60

main_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📚 Получить расписание"), KeyboardButton(text="👩‍🏫 Просмотреть список учителей")],
        [KeyboardButton(text="🗣️ Устное собеседование"), KeyboardButton(text="📖 ОГЭ")]
    ],
    resize_keyboard=True
)

async def auto_update():
    while True:
        try:
            updated = get_images(update=True)
            if updated:
                print("📢 Автообновление: новые фото загружены! Отправляю рассылку...")
                with sqlite3.connect("users.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM mailing_list")
                    users = cursor.fetchall()
                    print(users)
                    for user_id in users:
                        media = []
                        image_files = [f for f in os.listdir(TMP_PATH) if f.lower().endswith(".jpg")]
                        for filename in image_files:
                            file_path = os.path.join(TMP_PATH, filename)
                            media.append(InputMediaPhoto(media=FSInputFile(file_path)))

                        user_id = str(user_id)
                        user_id = user_id.replace('(', '').replace(')', '')
                        await bot.send_media_group(user_id, media)
                        kb = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="Да", callback_data="subscribe_on_mailing_callback")],
                                [InlineKeyboardButton(text="Нет", callback_data="unsubscribe_on_mailing_callback")],
                            ]
                        )
                    
                        # await message.answer(schedule_message, reply_markup=kb)
                        await asyncio.sleep(0.05)  # 50 мс пауза
                    conn.commit()
            else:
                print("ℹ️ Автообновление: новых фото нет.")
        except Exception as e:
            print("❌ Ошибка при автообновлении:", e)
        await asyncio.sleep(UPDATE_INTERVAL)


@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer(welcome_message, parse_mode="HTML", reply_markup=main_kb)


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


def subscribe_on_mailing(user_id: int):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO mailing_list (user_id) VALUES (?)", (user_id,))
        
        conn.commit()

def unsubscribe_on_mailing(user_id: int):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mailing_list WHERE user_id = ?", (user_id,))
        conn.commit()

# -------------------------------
#        /schedule
# -------------------------------
@dp.message(F.text == "/schedule")
async def cmd_schedule(message: types.Message):
    image_files = [f for f in os.listdir(TMP_PATH) if f.lower().endswith(".jpg")]

    if not image_files:
        get_images()
        image_files = [f for f in os.listdir(TMP_PATH) if f.lower().endswith(".jpg")]

    if not image_files:
        await message.answer("Изображения не найдены 😕")
        return

    media = []
    for filename in image_files:
        file_path = os.path.join(TMP_PATH, filename)
        media.append(InputMediaPhoto(media=FSInputFile(file_path)))

    await bot.send_media_group(message.chat.id, media)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="subscribe_on_mailing_callback")],
            [InlineKeyboardButton(text="Нет", callback_data="unsubscribe_on_mailing_callback")],
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



@dp.callback_query(F.data == "subscribe_on_mailing_callback")
async def callback_handler(callback: types.CallbackQuery):
    print("ale")
    subscribe_on_mailing(callback.from_user.id)
    await callback.answer("Вы подписались на рассылку")

@dp.callback_query(F.data == "unsubscribe_on_mailing_callback")
async def callback_handler(callback: types.CallbackQuery):
    unsubscribe_on_mailing(callback.from_user.id)
    await callback.answer("Вы отписались от рассылки")

@dp.message(F.text)
async def handle_inline(message: types.Message):
    if (message.text == "📚 Получить расписание"):
        await cmd_schedule(message)
    elif (message.text == "👩‍🏫 Просмотреть список учителей"):
        await cmd_teachers(message)
    elif (message.text == "🗣️ Устное собеседование"):
        await cmd_interview(message)
    elif (message.text == "📖 ОГЭ"):
        await cmd_oge(message)

async def main():
    asyncio.create_task(auto_update()) # автообновление

    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


