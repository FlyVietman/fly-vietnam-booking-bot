import asyncio
import logging
import os
from typing import Dict

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "https://wa.me/84345779540")
INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/flynhatrangru/")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/flynhatrang")

LANG_RU = "ru"
LANG_EN = "en"
LANG_VI = "vi"
DEFAULT_LANG = LANG_RU

USER_LANG: Dict[int, str] = {}

router = Router()


def get_lang(user_id: int) -> str:
    return USER_LANG.get(user_id, DEFAULT_LANG)


def set_lang(user_id: int, lang: str) -> None:
    USER_LANG[user_id] = lang


TEXTS = {
    LANG_RU: {
        "language_prompt": "Выберите язык / Choose language / Chọn ngôn ngữ",
        "welcome": (
            "Привет! 👋\n\n"
            "Это бот Fly Vietnam Booking для бронирования полётов и быстрой информации.\n\n"
            "Здесь можно:\n"
            "• узнать цены\n"
            "• понять, как проходит полёт\n"
            "• оставить заявку\n"
            "• быстро перейти в WhatsApp\n\n"
            "Выбирай нужный раздел ниже."
        ),
        "menu_book": "🪂 Забронировать полёт",
        "menu_prices": "💰 Цены",
        "menu_how": "📍 Как проходит",
        "menu_transfer": "🚗 Трансфер",
        "menu_media": "🎥 Фото и видео",
        "menu_faq": "❓ Частые вопросы",
        "menu_whatsapp": "📲 WhatsApp",
        "menu_instagram": "📸 Instagram",
        "menu_channel": "📢 Telegram-канал",
        "menu_main": "🏠 В главное меню",
        "cta_book": "🪂 Перейти к бронированию",
        "cta_whatsapp": "📲 Написать в WhatsApp",
        "cta_whatsapp_urgent": "📲 Срочно написать в WhatsApp",
        "prices_text": (
            "💰 Цены 2026\n\n"
            "🪂 Параплан — 2,990,000 VND\n"
            "🎥 FlyCam — 690,000 VND\n"
            "🎬 FlyCam Video — 990,000 VND\n"
            "🚀 Парамотор Standard — 2,990,000 VND\n"
            "🔥 Парамотор Premium — 3,990,000 VND\n"
            "🌙 Парамотор Night — 4,990,000 VND\n\n"
            "Для бронирования нажмите кнопку ниже."
        ),
        "how_text": (
            "📍 Как проходит полёт\n\n"
            "1. Вы оставляете заявку\n"
            "2. Мы подтверждаем дату и время\n"
            "3. Машина забирает вас из города Нячанг\n"
            "4. На месте проходит инструктаж\n"
            "5. Вы летите в тандеме с пилотом\n"
            "6. После полёта получаете эмоции, фото и видео"
        ),
        "transfer_text": (
            "🚗 Трансфер\n\n"
            "Трансфер из города Нячанг до клуба и обратно включён в стоимость.\n\n"
            "Из Камрани возможна доплата, если нужна отдельная логистика.\n\n"
            "После бронирования мы связываемся с вами и сообщаем точное время выезда."
        ),
        "media_text": (
            "🎥 Фото и видео\n\n"
            "Можно добавить съёмку FlyCam или видео-версию FlyCam Video.\n\n"
            "Наличие и формат лучше уточнять заранее при бронировании."
        ),
        "faq_text": (
            "❓ Частые вопросы\n\n"
            "• Это безопасно?\n"
            "Полёт проходит с профессиональным пилотом и инструктажем.\n\n"
            "• Можно без опыта?\n"
            "Да, это тандемный полёт.\n\n"
            "• Что надеть?\n"
            "Удобную одежду и кроссовки. Без шлёпанцев.\n\n"
            "• Можно детям?\n"
            "Уточняется индивидуально по погоде, весу и условиям полёта.\n\n"
            "• Что если плохая погода?\n"
            "Мы предложим перенос времени или даты.\n\n"
            "• Сколько длится полёт?\n"
            "Зависит от формата и погодных условий.\n\n"
            "• Когда лучше бронировать?\n"
            "Чем раньше, тем лучше. Хорошие слоты быстро заканчиваются."
        ),
        "choose_activity": "Выберите тип полёта:",
        "flight_paragliding": "🪂 Параплан",
        "flight_paramotor_std": "🚀 Парамотор Standard",
        "flight_paramotor_premium": "🔥 Парамотор Premium",
        "flight_paramotor_night": "🌙 Парамотор Night",
        "flight_solo": "🧑‍✈️ Соло пилоты",
        "ask_date": "Напишите желаемую дату полёта. Например: 13 April",
        "ask_time": "Напишите удобное время. Например: 10:00",
        "ask_guests": "Сколько гостей будет?",
        "ask_name": "Напишите имя и фамилию основного гостя",
        "ask_phone": "Напишите телефон или WhatsApp",
        "ask_hotel": "Напишите название отеля",
        "ask_note": "Комментарий или пожелания. Если нет, напишите: -",
        "thanks": (
            "Спасибо! ✅\n\n"
            "Заявка отправлена. Мы свяжемся с вами для подтверждения времени полёта.\n\n"
            "Если вопрос срочный, нажмите кнопку ниже."
        ),
        "admin_title": "🔥 Новая заявка из Telegram-бота",
        "admin_language": "Язык",
        "admin_activity": "Тип полёта",
        "admin_date": "Дата",
        "admin_time": "Время",
        "admin_guests": "Количество гостей",
        "admin_name": "Имя",
        "admin_phone": "Телефон / WhatsApp",
        "admin_hotel": "Отель",
        "admin_note": "Комментарий",
        "admin_user_id": "User ID",
        "admin_username": "Username",
        "lang_name": "Русский",
        "fallback": "Я пока не понял запрос. Нажмите /start и выберите нужный раздел в меню.",
    },
    LANG_EN: {
        "language_prompt": "Выберите язык / Choose language / Chọn ngôn ngữ",
        "welcome": (
            "Hello! 👋\n\n"
            "This is the Fly Vietnam Booking bot for flight booking and quick information.\n\n"
            "Here you can:\n"
            "• check prices\n"
            "• see how the flight works\n"
            "• send a booking request\n"
            "• quickly open WhatsApp\n\n"
            "Choose the section below."
        ),
        "menu_book": "🪂 Book a flight",
        "menu_prices": "💰 Prices",
        "menu_how": "📍 How it works",
        "menu_transfer": "🚗 Transfer",
        "menu_media": "🎥 Photo & Video",
        "menu_faq": "❓ FAQ",
        "menu_whatsapp": "📲 WhatsApp",
        "menu_instagram": "📸 Instagram",
        "menu_channel": "📢 Telegram channel",
        "menu_main": "🏠 Main menu",
        "cta_book": "🪂 Go to booking",
        "cta_whatsapp": "📲 Contact on WhatsApp",
        "cta_whatsapp_urgent": "📲 Contact us on WhatsApp",
        "prices_text": (
            "💰 Prices 2026\n\n"
            "🪂 Paragliding — 2,990,000 VND\n"
            "🎥 FlyCam — 690,000 VND\n"
            "🎬 FlyCam Video — 990,000 VND\n"
            "🚀 Paramotor Standard — 2,990,000 VND\n"
            "🔥 Paramotor Premium — 3,990,000 VND\n"
            "🌙 Paramotor Night — 4,990,000 VND\n\n"
            "Tap the button below to book your flight."
        ),
        "how_text": (
            "📍 How the flight works\n\n"
            "1. You send a booking request\n"
            "2. We confirm the date and time\n"
            "3. Our car picks you up in Nha Trang city\n"
            "4. You receive a briefing on site\n"
            "5. You fly in tandem with a pilot\n"
            "6. After the flight, you get emotions, photos and videos"
        ),
        "transfer_text": (
            "🚗 Transfer\n\n"
            "Transfer from Nha Trang city to the club and back is included in the price.\n\n"
            "An extra charge may apply for Cam Ranh, depending on the route.\n\n"
            "After booking, we contact you and confirm the exact pick-up time."
        ),
        "media_text": (
            "🎥 Photo and video\n\n"
            "You can add FlyCam shooting or the FlyCam Video option.\n\n"
            "Availability and format are best confirmed in advance during booking."
        ),
        "faq_text": (
            "❓ FAQ\n\n"
            "• Is it safe?\n"
            "The flight is conducted with a professional pilot and briefing.\n\n"
            "• Can I fly without experience?\n"
            "Yes, it is a tandem flight.\n\n"
            "• What should I wear?\n"
            "Comfortable clothes and sneakers. No flip-flops.\n\n"
            "• Can children fly?\n"
            "This is discussed individually depending on weather, weight and conditions.\n\n"
            "• What if the weather is bad?\n"
            "We will offer a new time or another date.\n\n"
            "• How long is the flight?\n"
            "It depends on the format and weather conditions.\n\n"
            "• When should I book?\n"
            "The earlier the better. Good slots fill up quickly."
        ),
        "choose_activity": "Choose flight type:",
        "flight_paragliding": "🪂 Paragliding",
        "flight_paramotor_std": "🚀 Paramotor Standard",
        "flight_paramotor_premium": "🔥 Paramotor Premium",
        "flight_paramotor_night": "🌙 Paramotor Night",
        "flight_solo": "🧑‍✈️ Solo pilots",
        "ask_date": "Enter your preferred flight date. Example: 13 April",
        "ask_time": "Enter your preferred time. Example: 10:00",
        "ask_guests": "How many guests?",
        "ask_name": "Enter the main guest’s full name",
        "ask_phone": "Enter phone number or WhatsApp",
        "ask_hotel": "Enter hotel name",
        "ask_note": "Comment or request. If none, write: -",
        "thanks": (
            "Thank you! ✅\n\n"
            "Your request has been sent. We will contact you to confirm the flight time.\n\n"
            "If your question is urgent, tap the button below."
        ),
        "admin_title": "🔥 New booking from Telegram bot",
        "admin_language": "Language",
        "admin_activity": "Flight type",
        "admin_date": "Date",
        "admin_time": "Time",
        "admin_guests": "Guests",
        "admin_name": "Name",
        "admin_phone": "Phone / WhatsApp",
        "admin_hotel": "Hotel",
        "admin_note": "Comment",
        "admin_user_id": "User ID",
        "admin_username": "Username",
        "lang_name": "English",
        "fallback": "I did not understand the request. Press /start and choose a section from the menu.",
    },
    LANG_VI: {
        "language_prompt": "Выберите язык / Choose language / Chọn ngôn ngữ",
        "welcome": (
            "Xin chào! 👋\n\n"
            "Đây là bot Fly Vietnam Booking để đặt chuyến bay và nhận thông tin nhanh.\n\n"
            "Tại đây bạn có thể:\n"
            "• xem giá\n"
            "• tìm hiểu quy trình bay\n"
            "• gửi yêu cầu đặt chỗ\n"
            "• nhanh chóng mở WhatsApp\n\n"
            "Hãy chọn mục bên dưới."
        ),
        "menu_book": "🪂 Đặt chuyến bay",
        "menu_prices": "💰 Giá",
        "menu_how": "📍 Quy trình",
        "menu_transfer": "🚗 Đưa đón",
        "menu_media": "🎥 Ảnh & Video",
        "menu_faq": "❓ Câu hỏi thường gặp",
        "menu_whatsapp": "📲 WhatsApp",
        "menu_instagram": "📸 Instagram",
        "menu_channel": "📢 Kênh Telegram",
        "menu_main": "🏠 Về menu chính",
        "cta_book": "🪂 Đi đến đặt chỗ",
        "cta_whatsapp": "📲 Liên hệ qua WhatsApp",
        "cta_whatsapp_urgent": "📲 Liên hệ ngay qua WhatsApp",
        "prices_text": (
            "💰 Bảng giá 2026\n\n"
            "🪂 Dù lượn đôi — 2,990,000 VND\n"
            "🎥 FlyCam — 690,000 VND\n"
            "🎬 FlyCam Video — 990,000 VND\n"
            "🚀 Paramotor Standard — 2,990,000 VND\n"
            "🔥 Paramotor Premium — 3,990,000 VND\n"
            "🌙 Paramotor Night — 4,990,000 VND\n\n"
            "Bấm nút bên dưới để đặt chuyến bay."
        ),
        "how_text": (
            "📍 Quy trình chuyến bay\n\n"
            "1. Bạn gửi yêu cầu đặt chỗ\n"
            "2. Chúng tôi xác nhận ngày và giờ\n"
            "3. Xe sẽ đón bạn trong thành phố Nha Trang\n"
            "4. Bạn sẽ được hướng dẫn tại điểm bay\n"
            "5. Bạn bay đôi cùng phi công\n"
            "6. Sau chuyến bay, bạn sẽ có trải nghiệm, ảnh và video"
        ),
        "transfer_text": (
            "🚗 Đưa đón\n\n"
            "Đưa đón từ thành phố Nha Trang đến câu lạc bộ và quay về đã bao gồm trong giá.\n\n"
            "Nếu đón tại Cam Ranh, có thể phát sinh phụ phí tùy theo lộ trình.\n\n"
            "Sau khi đặt chỗ, chúng tôi sẽ liên hệ và xác nhận thời gian đón chính xác."
        ),
        "media_text": (
            "🎥 Ảnh và video\n\n"
            "Bạn có thể thêm dịch vụ FlyCam hoặc FlyCam Video.\n\n"
            "Tình trạng còn chỗ và định dạng quay nên được xác nhận trước khi đặt chuyến bay."
        ),
        "faq_text": (
            "❓ Câu hỏi thường gặp\n\n"
            "• Có an toàn không?\n"
            "Chuyến bay được thực hiện cùng phi công chuyên nghiệp và có hướng dẫn trước khi bay.\n\n"
            "• Tôi có thể bay nếu chưa có kinh nghiệm không?\n"
            "Có, đây là chuyến bay đôi.\n\n"
            "• Nên mặc gì?\n"
            "Quần áo thoải mái và giày thể thao. Không đi dép.\n\n"
            "• Trẻ em có thể bay không?\n"
            "Sẽ được xem xét tùy theo thời tiết, cân nặng và điều kiện bay.\n\n"
            "• Nếu thời tiết xấu thì sao?\n"
            "Chúng tôi sẽ đề xuất đổi giờ hoặc đổi ngày.\n\n"
            "• Chuyến bay kéo dài bao lâu?\n"
            "Phụ thuộc vào loại chuyến bay và điều kiện thời tiết.\n\n"
            "• Nên đặt trước khi nào?\n"
            "Càng sớm càng tốt. Những khung giờ đẹp thường hết nhanh."
        ),
        "choose_activity": "Chọn loại chuyến bay:",
        "flight_paragliding": "🪂 Dù lượn đôi",
        "flight_paramotor_std": "🚀 Paramotor Standard",
        "flight_paramotor_premium": "🔥 Paramotor Premium",
        "flight_paramotor_night": "🌙 Paramotor Night",
        "flight_solo": "🧑‍✈️ Phi công solo",
        "ask_date": "Nhập ngày bay mong muốn. Ví dụ: 13 April",
        "ask_time": "Nhập giờ phù hợp. Ví dụ: 10:00",
        "ask_guests": "Có bao nhiêu khách?",
        "ask_name": "Nhập họ tên khách chính",
        "ask_phone": "Nhập số điện thoại hoặc WhatsApp",
        "ask_hotel": "Nhập tên khách sạn",
        "ask_note": "Ghi chú hoặc yêu cầu. Nếu không có, hãy nhập: -",
        "thanks": (
            "Cảm ơn bạn! ✅\n\n"
            "Yêu cầu của bạn đã được gửi. Chúng tôi sẽ liên hệ để xác nhận thời gian bay.\n\n"
            "Nếu cần gấp, hãy bấm nút bên dưới."
        ),
        "admin_title": "🔥 Yêu cầu mới từ Telegram bot",
        "admin_language": "Ngôn ngữ",
        "admin_activity": "Loại chuyến bay",
        "admin_date": "Ngày",
        "admin_time": "Giờ",
        "admin_guests": "Số khách",
        "admin_name": "Tên",
        "admin_phone": "Điện thoại / WhatsApp",
        "admin_hotel": "Khách sạn",
        "admin_note": "Ghi chú",
        "admin_user_id": "User ID",
        "admin_username": "Username",
        "lang_name": "Tiếng Việt",
        "fallback": "Tôi chưa hiểu yêu cầu. Hãy nhấn /start và chọn mục trong menu.",
    },
}


class BookingStates(StatesGroup):
    activity = State()
    date = State()
    time = State()
    guests = State()
    full_name = State()
    phone = State()
    hotel = State()
    note = State()


FLIGHT_TITLES = {
    LANG_RU: {
        "paragliding": TEXTS[LANG_RU]["flight_paragliding"],
        "paramotor_std": TEXTS[LANG_RU]["flight_paramotor_std"],
        "paramotor_premium": TEXTS[LANG_RU]["flight_paramotor_premium"],
        "paramotor_night": TEXTS[LANG_RU]["flight_paramotor_night"],
        "solo": TEXTS[LANG_RU]["flight_solo"],
    },
    LANG_EN: {
        "paragliding": TEXTS[LANG_EN]["flight_paragliding"],
        "paramotor_std": TEXTS[LANG_EN]["flight_paramotor_std"],
        "paramotor_premium": TEXTS[LANG_EN]["flight_paramotor_premium"],
        "paramotor_night": TEXTS[LANG_EN]["flight_paramotor_night"],
        "solo": TEXTS[LANG_EN]["flight_solo"],
    },
    LANG_VI: {
        "paragliding": TEXTS[LANG_VI]["flight_paragliding"],
        "paramotor_std": TEXTS[LANG_VI]["flight_paramotor_std"],
        "paramotor_premium": TEXTS[LANG_VI]["flight_paramotor_premium"],
        "paramotor_night": TEXTS[LANG_VI]["flight_paramotor_night"],
        "solo": TEXTS[LANG_VI]["flight_solo"],
    },
}


def language_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский", callback_data="lang:ru")
    kb.button(text="🇬🇧 English", callback_data="lang:en")
    kb.button(text="🇻🇳 Tiếng Việt", callback_data="lang:vi")
    kb.adjust(1)
    return kb.as_markup()


def main_menu(user_id: int) -> InlineKeyboardMarkup:
    lang = get_lang(user_id)
    t = TEXTS[lang]

    kb = InlineKeyboardBuilder()
    kb.button(text=t["menu_book"], callback_data="menu:book")
    kb.button(text=t["menu_prices"], callback_data="menu:prices")
    kb.button(text=t["menu_how"], callback_data="menu:how")
    kb.button(text=t["menu_transfer"], callback_data="menu:transfer")
    kb.button(text=t["menu_media"], callback_data="menu:media")
    kb.button(text=t["menu_faq"], callback_data="menu:faq")
    kb.button(text=t["menu_whatsapp"], url=WHATSAPP_URL)
    kb.button(text=t["menu_instagram"], url=INSTAGRAM_URL)
    kb.button(text=t["menu_channel"], url=CHANNEL_URL)
    kb.adjust(1)
    return kb.as_markup()


def info_keyboard(user_id: int) -> InlineKeyboardMarkup:
    lang = get_lang(user_id)
    t = TEXTS[lang]

    kb = InlineKeyboardBuilder()
    kb.button(text=t["cta_book"], callback_data="menu:book")
    kb.button(text=t["cta_whatsapp"], url=WHATSAPP_URL)
    kb.button(text=t["menu_main"], callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def post_booking_keyboard(user_id: int) -> InlineKeyboardMarkup:
    lang = get_lang(user_id)
    t = TEXTS[lang]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["cta_whatsapp_urgent"], url=WHATSAPP_URL)],
            [InlineKeyboardButton(text=t["menu_main"], callback_data="menu:home")],
        ]
    )


def flight_keyboard(user_id: int) -> InlineKeyboardMarkup:
    lang = get_lang(user_id)
    t = TEXTS[lang]

    kb = InlineKeyboardBuilder()
    kb.button(text=t["flight_paragliding"], callback_data="flight:paragliding")
    kb.button(text=t["flight_paramotor_std"], callback_data="flight:paramotor_std")
    kb.button(text=t["flight_paramotor_premium"], callback_data="flight:paramotor_premium")
    kb.button(text=t["flight_paramotor_night"], callback_data="flight:paramotor_night")
    kb.button(text=t["flight_solo"], callback_data="flight:solo")
    kb.button(text=t["menu_main"], callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def admin_booking_text(data: Dict[str, str], lang: str, user_id: int, username: str | None) -> str:
    t = TEXTS[lang]
    uname = f"@{username}" if username else "-"

    return (
        f"{t['admin_title']}\n\n"
        f"{t['admin_language']}: {TEXTS[lang]['lang_name']}\n"
        f"{t['admin_activity']}: {data.get('activity', '-')}\n"
        f"{t['admin_date']}: {data.get('date', '-')}\n"
        f"{t['admin_time']}: {data.get('time', '-')}\n"
        f"{t['admin_guests']}: {data.get('guests', '-')}\n"
        f"{t['admin_name']}: {data.get('full_name', '-')}\n"
        f"{t['admin_phone']}: {data.get('phone', '-')}\n"
        f"{t['admin_hotel']}: {data.get('hotel', '-')}\n"
        f"{t['admin_note']}: {data.get('note', '-')}\n\n"
        f"{t['admin_user_id']}: {user_id}\n"
        f"{t['admin_username']}: {uname}"
    )


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(TEXTS[DEFAULT_LANG]["language_prompt"], reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def set_language_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = callback.data.split(":", 1)[1]
    set_lang(callback.from_user.id, lang)
    t = TEXTS[lang]
    await callback.message.answer(t["welcome"], reply_markup=main_menu(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "menu:home")
async def home_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    await callback.message.answer(t["welcome"], reply_markup=main_menu(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "menu:prices")
async def prices_handler(callback: CallbackQuery) -> None:
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    await callback.message.answer(t["prices_text"], reply_markup=info_keyboard(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "menu:how")
async def how_handler(callback: CallbackQuery) -> None:
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    await callback.message.answer(t["how_text"], reply_markup=info_keyboard(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "menu:transfer")
async def transfer_handler(callback: CallbackQuery) -> None:
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    await callback.message.answer(t["transfer_text"], reply_markup=info_keyboard(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "menu:media")
async def media_handler(callback: CallbackQuery) -> None:
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    await callback.message.answer(t["media_text"], reply_markup=info_keyboard(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "menu:faq")
async def faq_handler(callback: CallbackQuery) -> None:
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    await callback.message.answer(t["faq_text"], reply_markup=info_keyboard(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "menu:book")
async def book_start_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    await state.set_state(BookingStates.activity)
    await callback.message.answer(t["choose_activity"], reply_markup=flight_keyboard(callback.from_user.id))
    await callback.answer()


@router.callback_query(BookingStates.activity, F.data.startswith("flight:"))
async def booking_activity_handler(callback: CallbackQuery, state: FSMContext) -> None:
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    key = callback.data.split(":", 1)[1]
    activity = FLIGHT_TITLES[lang].get(key, key)

    await state.update_data(activity=activity, language=TEXTS[lang]["lang_name"])
    await state.set_state(BookingStates.date)
    await callback.message.answer(t["ask_date"])
    await callback.answer()


@router.message(BookingStates.date)
async def booking_date_handler(message: Message, state: FSMContext) -> None:
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]
    await state.update_data(date=message.text.strip())
    await state.set_state(BookingStates.time)
    await message.answer(t["ask_time"])


@router.message(BookingStates.time)
async def booking_time_handler(message: Message, state: FSMContext) -> None:
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]
    await state.update_data(time=message.text.strip())
    await state.set_state(BookingStates.guests)
    await message.answer(t["ask_guests"])


@router.message(BookingStates.guests)
async def booking_guests_handler(message: Message, state: FSMContext) -> None:
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]
    await state.update_data(guests=message.text.strip())
    await state.set_state(BookingStates.full_name)
    await message.answer(t["ask_name"])


@router.message(BookingStates.full_name)
async def booking_name_handler(message: Message, state: FSMContext) -> None:
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]
    await state.update_data(full_name=message.text.strip())
    await state.set_state(BookingStates.phone)
    await message.answer(t["ask_phone"])


@router.message(BookingStates.phone)
async def booking_phone_handler(message: Message, state: FSMContext) -> None:
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]
    await state.update_data(phone=message.text.strip())
    await state.set_state(BookingStates.hotel)
    await message.answer(t["ask_hotel"])


@router.message(BookingStates.hotel)
async def booking_hotel_handler(message: Message, state: FSMContext) -> None:
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]
    await state.update_data(hotel=message.text.strip())
    await state.set_state(BookingStates.note)
    await message.answer(t["ask_note"])


@router.message(BookingStates.note)
async def booking_finish_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]
    await state.update_data(note=message.text.strip())
    data = await state.get_data()

    if ADMIN_CHAT_ID:
        admin_text = admin_booking_text(data, lang, message.from_user.id, message.from_user.username)
        await bot.send_message(ADMIN_CHAT_ID, admin_text)

    await message.answer(t["thanks"], reply_markup=post_booking_keyboard(message.from_user.id))
    await state.clear()


@router.message()
async def fallback_handler(message: Message) -> None:
    lang = get_lang(message.from_user.id)
    t = TEXTS[lang]
    await message.answer(t["fallback"], reply_markup=main_menu(message.from_user.id))


async def main() -> None:
    if BOT_TOKEN == "PASTE_BOT_TOKEN_HERE":
        raise ValueError("Set BOT_TOKEN environment variable or replace PASTE_BOT_TOKEN_HERE")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
