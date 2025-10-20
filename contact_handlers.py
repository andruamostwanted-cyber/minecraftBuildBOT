import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import TOKEN, ADMIN_IDS
from keyboards import get_main_keyboard, get_contact_cancel_keyboard


ADMINS = [ADMIN_IDS]


# Создаем роутер для обработки контактов
contact_router = Router()


# Фильтр для проверки прав администратора
def admin_filter(message: types.Message) -> bool:
    return ADMIN_IDS == message.from_user.id


# Состояния для FSM
class ContactStates(StatesGroup):
    waiting_for_message = State()

@contact_router.message(F.text == "📞 Связаться с нами")
async def contact_start_handler(message: types.Message, state: FSMContext):
    """Начало процесса связи с администратором"""
    await message.answer(
        "📞 <b>Связь с администратором</b>\n\n"
        "Напишите ваше сообщение, и мы ответим вам в ближайшее время.\n"
        "Вы можете задать вопрос, предложить идею или сообщить о проблеме.\n\n"
        "<i>Для отмены нажмите кнопку ниже</i>",
        reply_markup=get_contact_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ContactStates.waiting_for_message)

@contact_router.message(F.text == "❌ Отменить отправку")
async def contact_cancel_handler(message: types.Message, state: FSMContext):
    """Отмена отправки сообщения"""
    await state.clear()
    await message.answer(
        "❌ Отправка сообщения отменена.",
        reply_markup=get_main_keyboard()
    )

@contact_router.message(ContactStates.waiting_for_message)
async def process_contact_message(message: types.Message, state: FSMContext):
    """Обработка сообщения от пользователя и пересылка админам"""
    try:
        user = message.from_user
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        
        # Формируем сообщение для админа
        admin_message = (
            "📨 <b>Новое сообщение от пользователя</b>\n\n"
            f"<b>Пользователь:</b> {user_info}\n"
            f"<b>Имя:</b> {user.first_name} {user.last_name or ''}\n"
            f"<b>ID:</b> <code>{user.id}</code>\n\n"
            f"<b>Сообщение:</b>\n{message.text}"
        )
        
        # Отправляем сообщение всем администраторам
        sent_to_admins = []
        for admin_id in ADMINS:
            try:
                await message.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode="HTML"
                )
                sent_to_admins.append(admin_id)
            except Exception as e:
                logging.error(f"Error sending message to admin {admin_id}: {e}")
        
        if sent_to_admins:
            await message.answer(
                "✅ <b>Ваше сообщение отправлено администратору!</b>\n\n"
                "Мы ответим вам в ближайшее время.",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Не удалось отправить сообщение</b>\n\n"
                "Попробуйте позже или свяжитесь другим способом.",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        print("------>ОТПРАВЛЕНО СООБЩЕНИЕ!<------")
        
        await state.clear()
        
    except Exception as e:
        logging.error(f"Error processing contact message: {e}")
        await message.answer(
            "❌ Произошла ошибка при отправке сообщения.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

# Обработчик для ответа администратора пользователю
@contact_router.message(F.reply_to_message & F.text, admin_filter)
async def admin_reply_handler(message: types.Message):
    """Обработчик ответа администратора на сообщение пользователя"""
    # Сначала проверяем, что отправитель - администратор
    if not admin_filter(message):
        return
        
    try:
        replied_message = message.reply_to_message
        if not replied_message:
            return
        
        # Ищем ID пользователя в тексте сообщения разными способами
        user_id = None
        
        # Способ 1: Ищем в формате "ID: 123456"
        if replied_message.text:
            import re
            # Пробуем разные паттерны
            patterns = [
                r'ID:\s*<code>(\d+)</code>',
                r'ID:\s*(\d+)',
                r'ID\s*(\d+)',
                r'ID[\s:]*(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, replied_message.text)
                if match:
                    user_id = int(match.group(1))
                    break
        
        # Способ 2: Если не нашли в тексте, попробуем извлечь из entities
        if not user_id and replied_message.entities:
            for entity in replied_message.entities:
                if entity.type == "code":
                    code_text = replied_message.text[entity.offset:entity.offset + entity.length]
                    if code_text.isdigit():
                        user_id = int(code_text)
                        break
        
        # Способ 3: Посмотрим в caption если есть фото/документ
        if not user_id and replied_message.caption:
            import re
            match = re.search(r'ID[\s:]*(\d+)', replied_message.caption)
            if match:
                user_id = int(match.group(1))
        
        if user_id:
            # Отправляем ответ пользователю
            try:
                await message.bot.send_message(
                    chat_id=user_id,
                    text=f"📩 <b>Ответ от администратора:</b>\n\n{message.text}",
                    parse_mode="HTML"
                )
                await message.answer("✅ Ответ отправлен пользователю")
            except Exception as e:
                logging.error(f"Error sending message to user {user_id}: {e}")
                await message.answer("❌ Не удалось отправить сообщение пользователю (возможно, он заблокировал бота)")
        else:
            # Если не нашли ID, покажем админу как вручную отправить сообщение
            await message.answer(
                "❌ Не удалось найти ID пользователя.\n\n"
                "Чтобы ответить вручную, используйте команду:\n"
                f"<code>/reply_user ID_пользователя ваш_текст</code>\n\n"
                "Пример:\n"
                f"<code>/reply_user 12345678 Привет! Спасибо за обращение.</code>",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logging.error(f"Error in admin_reply_handler: {e}")
        await message.answer("❌ Ошибка при обработке ответа")