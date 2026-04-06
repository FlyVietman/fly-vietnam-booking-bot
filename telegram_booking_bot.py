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

# ============================================================
# TELEGRAM BOOKING BOT FOR PARAGLIDING / PARAMOTOR
# aiogram 3.x
# ============================================================
# 1) Create bot in @BotFather and put token into BOT_TOKEN
# 2) Install deps: pip install -U aiogram python-dotenv
# 3) Run: python telegram_booking_bot.py
# 4) For production, deploy on Render / Railway / VPS
# ============================================================

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "https://wa.me/84345779540")
INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/flynhatrangru/")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/flynhatrang")


@dataclass
class BookingData:
    activity: str = "-"
    date: str = "-"
    time: str = "-"
    guests: str = "-"
    full_name: str = "-"
    phone: str = "-"
    hotel: str = "-"
    note: str = "-"


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


# ----------------------------
# Keyboards
# ----------------------------
def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🪂 Забронировать полёт", callback_data="book")
    kb.button(text="💰 Цены", callback_data="prices")
    kb.button(text="📍 Как проходит", callback_data="how_it_works")
    kb.button(text="🚗 Трансфер", callback_data="transfer")
    kb.button(text="🎥 Фото и видео", callback_data="media")
    kb.button(text="❓ Частые вопросы", callback_data="faq")
    kb.button(text="📲 WhatsApp", url=WHATSAPP_URL)
    kb.button(text="📸 Instagram", url=INSTAGRAM_URL)
    kb.button(text="📢 Telegram-канал", url=CHANNEL_URL)
    kb.adjust(1)
    return kb.as_markup()


def activity_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🪂 Параплан", callback_data="activity:Параплан")
    kb.button(text="🛩 Парамотор Standard", callback_data="activity:Парамотор Standard")
    kb.button(text="🌃 Парамотор Night", callback_data="activity:Парамотор Night")
    kb.adjust(1)
    return kb.as_markup()


def after_info_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🪂 Перейти к бронированию", callback_data="book")
    kb.button(text="📲 Написать в WhatsApp", url=WHATSAPP_URL)
    kb.adjust(1)
    return kb.as_markup()


# ----------------------------
# Helpers
# ----------------------------
def format_booking(data: Dict[str, str], user_id: int, username: Optional[str]) -> str:
    uname = f"@{username}" if username else "-"
    return (
        "🔥 Новая заявка из Telegram-бота\n\n"
        f"Тип полёта: {data.get('activity', '-')}\n"
        f"Дата: {data.get('date', '-')}\n"
        f"Время: {data.get('time', '-')}\n"
        f"Количество гостей: {data.get('guests', '-')}\n"
        f"Имя: {data.get('full_name', '-')}\n"
        f"Телефон / WhatsApp: {data.get('phone', '-')}\n"
        f"Отель: {data.get('hotel', '-')}\n"
        f"Комментарий: {data.get('note', '-')}\n\n"
        f"User ID: {user_id}\n"
        f"Username: {uname}"
    )


WELCOME_TEXT = (
    "Привет! 👋\n\n"
    "Это бот Fly Nha Trang для бронирования полётов и быстрой информации.\n\n"
    "Здесь можно:\n"
    "• узнать цены\n"
    "• понять, как проходит полёт\n"
    "• оставить заявку\n"
    "• быстро перейти в WhatsApp\n\n"
    "Выбирай нужный раздел ниже."
)

PRICES_TEXT = (
    "💰 Цены 2026\n\n"
    "🪂 Параплан: 2,990,000 VND\n"
    "🎥 FlyCam: 690,000 VND\n"
    "🎬 FlyCam Video: 990,000 VND\n"
    "🛩 Парамотор Standard: 2,990,000 VND\n"
    "✨ Парамотор Premium: 3,990,000 VND\n"
    "🌃 Парамотор Night: 4,990,000 VND\n\n"
    "Для бронирования нажми кнопку ниже."
)

HOW_IT_WORKS_TEXT = (
    "📍 Как проходит полёт\n\n"
    "1. Вы оставляете заявку\n"
    "2. Мы подтверждаем дату и время\n"
    "3. Машина забирает вас из города Нячанг\n"
    "4. На месте проходит инструктаж\n"
    "5. Вы летите в тандеме с пилотом\n"
    "6. После полёта получаете эмоции, фото и видео 😌"
)

TRANSFER_TEXT = (
    "🚗 Трансфер\n\n"
    "Трансфер из города Нячанг до клуба и обратно включён в стоимость.\n"
    "Из Камрани возможна доплата, если нужна индивидуальная логистика.\n\n"
    "После бронирования мы связываемся с вами и сообщаем точное время выезда."
)

MEDIA_TEXT = (
    "🎥 Фото и видео\n\n"
    "Можно добавить съёмку FlyCam или видео-версию.\n"
    "Наличие и формат лучше подтвердить заранее при бронировании."
)

FAQ_TEXT = (
    "❓ Частые вопросы\n\n"
    "• Это безопасно?\n"
    "Полёт проходит с профессиональным пилотом и инструктажем.\n\n"
    "• Можно без опыта?\n"
    "Да, это тандемный полёт.\n\n"
    "• Что надеть?\n"
    "Удобную одежду, кроссовки, без шлёпанцев.\n\n"
    "• Можно с детьми?\n"
    "Уточняется индивидуально по погоде, весу и условиям полёта."
)


# ----------------------------
# Handlers
# ----------------------------
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())


@router.callback_query(F.data == "prices")
async def prices_handler(callback: CallbackQuery) -> None:
    await callback.message.answer(PRICES_TEXT, reply_markup=after_info_keyboard())
    await callback.answer()


@router.callback_query(F.data == "how_it_works")
async def how_handler(callback: CallbackQuery) -> None:
    await callback.message.answer(HOW_IT_WORKS_TEXT, reply_markup=after_info_keyboard())
    await callback.answer()


@router.callback_query(F.data == "transfer")
async def transfer_handler(callback: CallbackQuery) -> None:
    await callback.message.answer(TRANSFER_TEXT, reply_markup=after_info_keyboard())
    await callback.answer()


@router.callback_query(F.data == "media")
async def media_handler(callback: CallbackQuery) -> None:
    await callback.message.answer(MEDIA_TEXT, reply_markup=after_info_keyboard())
    await callback.answer()


@router.callback_query(F.data == "faq")
async def faq_handler(callback: CallbackQuery) -> None:
    await callback.message.answer(FAQ_TEXT, reply_markup=after_info_keyboard())
    await callback.answer()


@router.callback_query(F.data == "book")
async def book_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BookingStates.activity)
    await callback.message.answer(
        "Выберите тип полёта:",
        reply_markup=activity_keyboard(),
    )
    await callback.answer()


@router.callback_query(BookingStates.activity, F.data.startswith("activity:"))
async def booking_activity(callback: CallbackQuery, state: FSMContext) -> None:
    activity = callback.data.split(":", 1)[1]
    await state.update_data(activity=activity)
    await state.set_state(BookingStates.date)
    await callback.message.answer("Напишите желаемую дату полёта. Например: 12 April")
    await callback.answer()


@router.message(BookingStates.date)
async def booking_date(message: Message, state: FSMContext) -> None:
    await state.update_data(date=message.text.strip())
    await state.set_state(BookingStates.time)
    await message.answer("Напишите удобное время. Например: 09:00")


@router.message(BookingStates.time)
async def booking_time(message: Message, state: FSMContext) -> None:
    await state.update_data(time=message.text.strip())
    await state.set_state(BookingStates.guests)
    await message.answer("Сколько гостей будет? Например: 2")


@router.message(BookingStates.guests)
async def booking_guests(message: Message, state: FSMContext) -> None:
    await state.update_data(guests=message.text.strip())
    await state.set_state(BookingStates.full_name)
    await message.answer("Напишите имя и фамилию основного гостя")


@router.message(BookingStates.full_name)
async def booking_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text.strip())
    await state.set_state(BookingStates.phone)
    await message.answer("Напишите телефон или WhatsApp")


@router.message(BookingStates.phone)
async def booking_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=message.text.strip())
    await state.set_state(BookingStates.hotel)
    await message.answer("Напишите название отеля")


@router.message(BookingStates.hotel)
async def booking_hotel(message: Message, state: FSMContext) -> None:
    await state.update_data(hotel=message.text.strip())
    await state.set_state(BookingStates.note)
    await message.answer("Комментарий или пожелания. Если нет, напишите: -")


@router.message(BookingStates.note)
async def booking_finish(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(note=message.text.strip())
    data = await state.get_data()

    text = format_booking(data, message.from_user.id, message.from_user.username)

    if ADMIN_CHAT_ID:
        await bot.send_message(ADMIN_CHAT_ID, text)

    await message.answer(
        "Спасибо! ✅\n\n"
        "Заявка отправлена. Мы свяжемся с вами для подтверждения времени полёта.\n\n"
        "Если вопрос срочный, нажмите кнопку ниже.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📲 Срочно написать в WhatsApp", url=WHATSAPP_URL)],
                [InlineKeyboardButton(text="🏠 В главное меню", callback_data="home")],
            ]
        ),
    )
    await state.clear()


@router.callback_query(F.data == "home")
async def home_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(WELCOME_TEXT, reply_markup=main_menu())
    await callback.answer()


@router.message()
async def fallback_handler(message: Message) -> None:
    await message.answer(
        "Я пока не понял запрос 🤖\n\n"
        "Нажмите /start и выберите нужный раздел в меню."
    )


async def main() -> None:
    if BOT_TOKEN == "PASTE_BOT_TOKEN_HERE":
        raise ValueError("Set BOT_TOKEN environment variable or replace PASTE_BOT_TOKEN_HERE")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
