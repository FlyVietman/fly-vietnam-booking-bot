import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Dict, Optional

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "https://wa.me/84345779540")
INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/flynhatrangru/")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/flynhatrang")

# ==============================
# LANGUAGE SUPPORT
# ==============================
LANG_RU = "ru"
LANG_VI = "vi"

USER_LANG: Dict[int, str] = {}


def get_lang(user_id: int) -> str:
    return USER_LANG.get(user_id, LANG_RU)


def set_lang(user_id: int, lang: str):
    USER_LANG[user_id] = lang


# ==============================
# TEXTS
# ==============================
TEXTS = {
    LANG_RU: {
        "welcome": (
            "Привет! 👋\n\n"
            "Это бот Fly Nha Trang для бронирования полётов.\n\n"
            "Выбирай нужный раздел ниже."
        ),
        "book": "🪂 Забронировать полёт",
        "prices": "💰 Цены",
        "how": "📍 Как проходит",
        "transfer": "🚗 Трансфер",
        "media": "🎥 Фото и видео",
        "faq": "❓ Частые вопросы",
        "choose_activity": "Выберите тип полёта:",
        "date": "Напишите дату полёта",
        "time": "Напишите время",
        "guests": "Сколько гостей?",
        "name": "Имя и фамилия",
        "phone": "Телефон / WhatsApp",
        "hotel": "Отель",
        "note": "Комментарий или -",
        "thanks": "Спасибо! Заявка отправлена",
    },
    LANG_VI: {
        "welcome": (
            "Xin chào! 👋\n\n"
            "Đây là bot đặt chuyến bay Fly Nha Trang.\n\n"
            "Chọn mục bên dưới."
        ),
        "book": "🪂 Đặt chuyến bay",
        "prices": "💰 Giá",
        "how": "📍 Quy trình",
        "transfer": "🚗 Đưa đón",
        "media": "🎥 Ảnh & Video",
        "faq": "❓ Câu hỏi",
        "choose_activity": "Chọn loại bay:",
        "date": "Nhập ngày bay",
        "time": "Nhập giờ",
        "guests": "Số khách",
        "name": "Tên khách",
        "phone": "Số điện thoại",
        "hotel": "Khách sạn",
        "note": "Ghi chú hoặc -",
        "thanks": "Cảm ơn! Đã gửi yêu cầu",
    },
}


# ==============================
# STATES
# ==============================
class BookingStates(StatesGroup):
    activity = State()
    date = State()
    time = State()
    guests = State()
    full_name = State()
    phone = State()
    hotel = State()
    note = State()


router = Router()


# ==============================
# KEYBOARDS
# ==============================
def language_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский", callback_data="lang:ru")
    kb.button(text="🇻🇳 Tiếng Việt", callback_data="lang:vi")
    kb.adjust(1)
    return kb.as_markup()


def main_menu(user_id: int):
    lang = get_lang(user_id)
    t = TEXTS[lang]

    kb = InlineKeyboardBuilder()
    kb.button(text=t["book"], callback_data="book")
    kb.button(text=t["prices"], callback_data="prices")
    kb.button(text=t["how"], callback_data="how")
    kb.button(text=t["transfer"], callback_data="transfer")
    kb.button(text=t["media"], callback_data="media")
    kb.button(text=t["faq"], callback_data="faq")
    kb.adjust(1)
    return kb.as_markup()


# ==============================
# HANDLERS
# ==============================
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите язык / Chọn ngôn ngữ:", reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split(":")[1]
    set_lang(callback.from_user.id, lang)

    t = TEXTS[lang]

    await callback.message.answer(t["welcome"], reply_markup=main_menu(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "book")
async def book_start(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]

    await state.set_state(BookingStates.activity)
    await callback.message.answer(t["choose_activity"])
    await callback.answer()


@router.message(BookingStates.activity)
async def booking_activity(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]

    await state.update_data(activity=message.text)
    await state.set_state(BookingStates.date)
    await message.answer(t["date"])


@router.message(BookingStates.date)
async def booking_date(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]

    await state.update_data(date=message.text)
    await state.set_state(BookingStates.time)
    await message.answer(t["time"])


@router.message(BookingStates.time)
async def booking_time(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]

    await state.update_data(time=message.text)
    await state.set_state(BookingStates.guests)
    await message.answer(t["guests"])


@router.message(BookingStates.guests)
async def booking_guests(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]

    await state.update_data(guests=message.text)
    await state.set_state(BookingStates.full_name)
    await message.answer(t["name"])


@router.message(BookingStates.full_name)
async def booking_name(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]

    await state.update_data(full_name=message.text)
    await state.set_state(BookingStates.phone)
    await message.answer(t["phone"])


@router.message(BookingStates.phone)
async def booking_phone(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]

    await state.update_data(phone=message.text)
    await state.set_state(BookingStates.hotel)
    await message.answer(t["hotel"])


@router.message(BookingStates.hotel)
async def booking_hotel(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]

    await state.update_data(hotel=message.text)
    await state.set_state(BookingStates.note)
    await message.answer(t["note"])


@router.message(BookingStates.note)
async def booking_finish(message: Message, state: FSMContext, bot: Bot):
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]

    data = await state.get_data()

    text = f"🔥 Booking\n\n{data}"

    if ADMIN_CHAT_ID:
        await bot.send_message(ADMIN_CHAT_ID, text)

    await message.answer(t["thanks"])
    await state.clear()


async def main():
    if BOT_TOKEN == "PASTE_BOT_TOKEN_HERE":
        raise ValueError("Set BOT_TOKEN")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
