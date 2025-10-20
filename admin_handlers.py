import asyncio
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from db.crud import build_crud, analytics_crud
from db.models import BuildType, BuildStyle, Difficulty, BUILD_TYPE_MAP, STYLE_MAP, DIFFICULTY_MAP
from keyboards import get_admin_keyboard, get_admin_builds_keyboard, get_admin_moderation_keyboard

# Создаем роутер для админ-панели
admin_router = Router()

# Фильтр для проверки прав администратора
def admin_filter(message: types.Message) -> bool:
    return ADMIN_IDS == message.from_user.id

# Состояния для FSM
class AdminStates(StatesGroup):
    waiting_build_name = State()
    waiting_build_description = State()
    waiting_build_url = State()
    waiting_build_image = State() 
    waiting_build_type = State()
    waiting_build_style = State()
    waiting_build_difficulty = State()

class NewsletterStates(StatesGroup):
    waiting_newsletter_message = State()

# Команда для админ-панели
@admin_router.message(Command("admin"), admin_filter)
async def admin_panel_handler(message: types.Message):
    """Обработчик команды /admin"""
    await message.answer(
        "🛠️ <b>Панель администратора</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )

# Обработчики админ-кнопок
@admin_router.message(F.text == "📊 Статистика", admin_filter)
async def admin_stats_handler(message: types.Message):
    """Статистика бота"""
    try:
        builds_count = await build_crud.get_builds_count()
        top_builds = await build_crud.get_top_builds(limit=3)
        
        stats_text = "📊 <b>Статистика бота</b>\n\n"
        stats_text += f"• Всего сборок: <b>{builds_count}</b>\n"
        
        if top_builds:
            stats_text += "\n<b>Топ-3 сборки:</b>\n"
            for i, build in enumerate(top_builds, 1):
                stats_text += f"{i}. {build.name} - {build.downloads_count} скачиваний\n"
        else:
            stats_text += "\nНет данных о сборках"
            
        await message.answer(stats_text, parse_mode="HTML")
        
    except Exception as e:
        logging.error(f"Error getting stats: {e}")
        await message.answer("❌ Ошибка при получении статистики")

@admin_router.message(F.text == "📦 Управление сборками", admin_filter)
async def admin_builds_handler(message: types.Message):
    """Управление сборками"""
    await message.answer(
        "📦 <b>Управление сборками</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_builds_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(F.text == "👁️ Просмотр всех сборок", admin_filter)
async def view_all_builds_handler(message: types.Message):
    """Просмотр всех сборок"""
    try:
        from db.crud import build_crud
        
        # Получаем все сборки (без лимита)
        builds = await build_crud.get_builds_by_filters(limit=50)
        
        if not builds:
            await message.answer("❌ В базе нет сборок")
            return
        
        text = "👁️ <b>Все сборки в базе:</b>\n\n"
        
        for i, build in enumerate(builds, 1):
            status = "✅" if build.is_approved else "⏳"
            text += f"{status} <b>{build.name}</b>\n"
            text += f"   ID: {build.id} | Скачиваний: {build.downloads_count}\n"
            text += f"   Тип: {build.build_type.value} | Стиль: {build.style.value}\n"
            
            if i % 5 == 0:  # Разбиваем на сообщения по 5 сборок
                await message.answer(text, parse_mode="HTML")
                text = ""
        
        if text.strip():  # Отправляем оставшиеся сборки
            await message.answer(text, parse_mode="HTML")
            
    except Exception as e:
        logging.error(f"Error viewing builds: {e}")
        await message.answer("❌ Ошибка при получении сборок")

@admin_router.message(F.text == "➕ Добавить сборку (admin)", admin_filter)
async def add_build_handler(message: types.Message, state: FSMContext):
    """Начало процесса добавления сборки"""
    await message.answer(
        "➕ <b>Добавление новой сборки</b>\n\n"
        "📝 <b>Процесс добавления:</b>\n"
        "1. Название сборки\n"
        "2. Описание\n" 
        "3. Ссылка для скачивания\n"
        "4. Ссылка на изображение (опционально)\n"
        "5. Тип, стиль и сложность\n\n"
        "Введите название сборки:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_build_name)

@admin_router.message(AdminStates.waiting_build_name, admin_filter)
async def process_build_name(message: types.Message, state: FSMContext):
    """Обработка названия сборки"""
    await state.update_data(name=message.text)
    await message.answer("📝 Введите описание сборки:")
    await state.set_state(AdminStates.waiting_build_description)

@admin_router.message(AdminStates.waiting_build_description, admin_filter)
async def process_build_description(message: types.Message, state: FSMContext):
    """Обработка описания сборки"""
    await state.update_data(description=message.text)
    await message.answer("🔗 Введите ссылку для скачивания:")
    await state.set_state(AdminStates.waiting_build_url)

@admin_router.message(AdminStates.waiting_build_url, admin_filter)
async def process_build_url(message: types.Message, state: FSMContext):
    """Обработка ссылки сборки"""
    # Проверяем что это похоже на URL
    if not message.text.startswith(('http://', 'https://')):
        await message.answer(
            "❌ <b>Это не похоже на ссылку!</b>\n\n"
            "Пожалуйста, введите корректную ссылку начинающуюся с http:// или https://",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(download_url=message.text)

    keyboard = [
        [types.KeyboardButton(text="🚫 Без изображения")],
        [types.KeyboardButton(text="❌ Отменить добавление")]
    ]
    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "🖼️ <b>Хотите добавить изображение для сборки?</b>\n\n"
        "Отправьте ссылку на изображение или нажмите \"🚫 Без изображения\"\n\n"
        "<i>Поддерживаются прямые ссылки на изображения (jpg, png)</i>",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_build_image)

@admin_router.message(AdminStates.waiting_build_image, admin_filter)
async def process_build_image(message: types.Message, state: FSMContext):
    """Обработка изображения сборки"""
    user_data = await state.get_data()
    
    try:
        if message.text == "🚫 Без изображения":
            image_url = None
            await message.answer(
                "✅ Продолжаем без изображения",
                reply_markup=types.ReplyKeyboardRemove()
            )
        elif message.text == "❌ Отменить добавление":
            await state.clear()
            await message.answer(
                "❌ Добавление сборки отменено",
                reply_markup=get_admin_builds_keyboard()
            )
            return
        else:
            # Проверяем что это похоже на URL изображения
            if message.text.startswith(('http://', 'https://')):
                image_url = message.text
                await message.answer(
                    "✅ Изображение принято!",
                    reply_markup=types.ReplyKeyboardRemove()
                )
            else:
                await message.answer(
                    "❌ <b>Это не похоже на ссылку на изображение!</b>\n\n"
                    "Пожалуйста, отправьте прямую ссылку на изображение (jpg, png) "
                    "или нажмите \"🚫 Без изображения\"",
                    parse_mode="HTML"
                )
                return
            await state.update_data(image_url=image_url)
    except Exception as e:
        await message.answer("❌ Произошла ошибка! Попробуйте повторить попытку.")
    
    # Переходим к выбору типа сборки
    from keyboards import get_admin_build_types_keyboard
    await message.answer(
        "🎯 <b>Выберите тип сборки:</b>\n\n"
        "<i>Какой игровой опыт предлагает сборка?</i>",
        reply_markup=get_admin_build_types_keyboard()
    )
    await state.set_state(AdminStates.waiting_build_type)

# Обработчики выбора типа, стиля и сложности с УНИКАЛЬНЫМИ callback data
@admin_router.callback_query(F.data.startswith("admin_type_"), AdminStates.waiting_build_type)
async def process_build_type(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора типа сборки"""
    build_type = callback.data.replace("admin_type_", "")
    await state.update_data(build_type=build_type)
    
    from keyboards import get_admin_style_keyboard
    await callback.message.edit_text(
        "🏰 Выберите стиль сборки:",
        reply_markup=get_admin_style_keyboard()
    )
    await state.set_state(AdminStates.waiting_build_style)
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin_style_"), AdminStates.waiting_build_style)
async def process_build_style(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора стиля сборки"""
    style = callback.data.replace("admin_style_", "")
    await state.update_data(style=style)
    
    from keyboards import get_admin_difficulty_keyboard
    await callback.message.edit_text(
        "⚡ Выберите сложность сборки:",
        reply_markup=get_admin_difficulty_keyboard()
    )
    await state.set_state(AdminStates.waiting_build_difficulty)
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin_difficulty_"), AdminStates.waiting_build_difficulty)
async def process_build_difficulty(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора сложности и сохранение сборки"""
    try:
        difficulty = callback.data.replace("admin_difficulty_", "")
        user_data = await state.get_data()
        
        # Создаем сборку в базе данных
        build = await build_crud.create_build(
            name=user_data['name'],
            description=user_data['description'],
            download_url=user_data['download_url'],
            build_type=BUILD_TYPE_MAP[user_data['build_type']],
            style=STYLE_MAP[user_data['style']],
            difficulty=DIFFICULTY_MAP[difficulty],
            image_url=user_data.get('image_url'),  # Добавляем изображение
            added_by=callback.from_user.id
        )
        
        # Формируем красивое сообщение о успешном добавлении
        success_text = (
            f"✅ <b>Сборка успешно добавлена!</b>\n\n"
            f"<b>Название:</b> {build.name}\n"
            f"<b>Тип:</b> {user_data['build_type']}\n"
            f"<b>Стиль:</b> {user_data['style']}\n"
            f"<b>Сложность:</b> {difficulty}\n"
        )
        
        if user_data.get('image_url'):
            success_text += f"<b>Изображение:</b> ✅ Добавлено\n"
        else:
            success_text += f"<b>Изображение:</b> ❌ Отсутствует\n"
            
        success_text += f"\n<b>ID сборки:</b> {build.id}"
        
        # Если есть изображение, отправляем его с текстом
        if user_data.get('image_url'):
            try:
                await callback.message.answer_photo(
                    photo=user_data['image_url'],
                    caption=success_text,
                    parse_mode="HTML",
                    reply_markup=get_admin_keyboard()
                )
            except Exception as e:
                logging.error(f"Error sending photo: {e}")
                await callback.message.answer(
                    f"{success_text}\n\n⚠️ <i>Не удалось загрузить изображение</i>",
                    parse_mode="HTML",
                    reply_markup=get_admin_keyboard()
                )
        else:
            await callback.message.answer(success_text, parse_mode="HTML", reply_markup=get_admin_keyboard())
        
        await state.clear()
        
    except Exception as e:
        logging.error(f"Error creating build: {e}")
        await callback.message.answer(
            f"❌ <b>Ошибка при создании сборки</b>\n\n"
            f"Ошибка: {str(e)}\n\n"
            f"Попробуйте еще раз.",
            parse_mode="HTML"
        )
        await state.clear()
    
    await callback.answer()

@admin_router.message(F.text == "❌ Удалить сборку", admin_filter)
async def delete_build_handler(message: types.Message):
    """Удаление сборки"""
    await message.answer(
        "❌ <b>Удаление сборки</b>\n\n"
        "Для удаления введите команду:\n"
        "<code>/delete_build ID_сборки</code>\n\n"
        "Например: <code>/delete_build 1</code>",
        parse_mode="HTML"
    )

@admin_router.message(Command("delete_build"), admin_filter)
async def delete_build_command(message: types.Message):
    """Команда удаления сборки по ID"""
    try:
        build_id = int(message.text.split()[1])
        build = await build_crud.get_build_by_id(build_id)
        
        if not build:
            await message.answer("❌ Сборка с таким ID не найдена")
            return
        
        # Здесь должна быть логика удаления (пока просто отмечаем как неодобренную)
        build.is_approved = False
        answer = await build_crud.delete_build(build_id=build_id)
        # В реальном приложении нужно добавить метод delete в CRUD
        
        if answer:
            await message.answer(f"✅ Сборка '{build.name}' удалена!")
        else:
            await message.answer(f"❌ Не удалось удалить сборку '{build.name}'!")

        print("-------->УДАЛЕНО!<---------")
        
    except (IndexError, ValueError):
        await message.answer("❌ Неверный формат команды. Используйте: /delete_build ID")
    except Exception as e:
        logging.error(f"Error deleting build: {e}")
        await message.answer("❌ Ошибка при удалении сборки")

@admin_router.message(F.text == "⏳ Модерация", admin_filter)
async def moderation_handler(message: types.Message):
    """Панель модерации"""
    # Здесь можно добавить логику для модерации пользовательских сборок
    await message.answer(
        "⏳ <b>Панель модерации</b>\n\n"
        "Здесь будут сборки, ожидающие модерации.\n"
        "Пока эта функция в разработке.",
        reply_markup=get_admin_moderation_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(F.text == "⬅️ Назад в админку", admin_filter)
async def back_to_admin_handler(message: types.Message):
    """Возврат в главное меню админ-панели"""
    await admin_panel_handler(message)

@admin_router.message(F.text == "🎮 Основное меню", admin_filter)
async def back_to_main_handler(message: types.Message, state: FSMContext):
    """Возврат в основное меню"""
    await state.clear()
    from handlers import start_handler
    await start_handler(message)

@admin_router.message(Command("contacts"), admin_filter)
async def contacts_stats_handler(message: types.Message):
    """Статистика контактов"""
    # Здесь можно добавить логику для отслеживания статистики сообщений
    await message.answer(
        "📞 <b>Система связи с пользователями</b>\n\n"
        "Пользователи могут отправлять сообщения через кнопку \"Связаться с нами\"\n\n"
        "<b>Как отвечать:</b>\n"
        "1. Просто ответьте (reply) на сообщение пользователя\n"
        "2. Бот автоматически перешлет ответ отправителю\n\n"
        "<b>Формат сообщений от пользователей:</b>\n"
        "• Имя и username пользователя\n"
        "• ID пользователя\n"
        "• Текст сообщения",
        parse_mode="HTML"
    )

# statistics
@admin_router.message(Command("stats"), admin_filter)
async def stats_handler(message: types.Message):
    """Статистика бота"""
    try:
        # Получаем статистику
        daily_stats = await analytics_crud.get_daily_stats()
        total_users = await analytics_crud.get_total_users()
        top_actions = await analytics_crud.get_top_actions(5)
        
        stats_text = (
            "📊 <b>СТАТИСТИКА БОТА</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>Дата:</b> {daily_stats['date']}\n"
            f"👥 <b>Всего пользователей:</b> {total_users}\n"
            f"🆕 <b>Новых сегодня:</b> {daily_stats['new_users']}\n"
            f"🔥 <b>Активных сегодня:</b> {daily_stats['active_users']}\n"
            f"📈 <b>Действий сегодня:</b> {daily_stats['total_actions']}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Топ-5 действий:</b>\n"
        )
        
        for action, count in top_actions:
            action_name = {
                'start': '🚀 Старт',
                'random_build': '🎲 Случайная сборка', 
                'build_filters': '🔍 Поиск по фильтрам',
                'contact': '📞 Связь с админом'
            }.get(action, action)
            
            stats_text += f"• {action_name}: {count}\n"
        
        await message.answer(stats_text, parse_mode="HTML")
        
    except Exception as e:
        logging.error(f"Error getting stats: {e}")
        await message.answer("❌ Ошибка при получении статистики")

@admin_router.message(Command("user_stats"), admin_filter)
async def user_stats_handler(message: types.Message):
    """Статистика по конкретному пользователю"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer(
                "❌ Неверный формат.\n"
                "Используйте: <code>/user_stats ID_пользователя</code>\n"
                "Пример: <code>/user_stats 123456789</code>",
                parse_mode="HTML"
            )
            return
        
        user_id = int(parts[1])
        stats = await analytics_crud.get_user_stats(user_id)
        
        if not stats['first_seen']:
            await message.answer(f"❌ Пользователь {user_id} не найден в статистике")
            return
        
        user_text = (
            f"👤 <b>Статистика пользователя</b> ID: {user_id}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>Первое действие:</b> {stats['first_seen'].timestamp.strftime('%d.%m.%Y %H:%M')}\n"
            f"🕒 <b>Последнее действие:</b> {stats['last_seen'].timestamp.strftime('%d.%m.%Y %H:%M')}\n"
            f"📊 <b>Всего действий:</b> {stats['total_actions']}\n"
            f"🎯 <b>Последнее действие:</b> {stats['last_seen'].action}\n"
        )
        
        await message.answer(user_text, parse_mode="HTML")
        
    except ValueError:
        await message.answer("❌ Неверный ID пользователя")
    except Exception as e:
        logging.error(f"Error getting user stats: {e}")
        await message.answer("❌ Ошибка при получении статистики пользователя")
#----------------------------
@admin_router.message(F.text == "🎺 Сделать рассылку", admin_filter)
async def newsletter_command(message: types.Message, state: FSMContext):
    """Команда для создания рассылки"""
    await message.answer(
        "📢 <b>Создание рассылки</b>\n\n"
        "Введите текст сообщения, которое будет отправлено всем пользователям:\n\n"
        "<i>Поддерживается HTML разметка</i>",
        parse_mode="HTML"
    )
    await state.set_state(NewsletterStates.waiting_newsletter_message)


# Обработчик текста рассылки
@admin_router.message(NewsletterStates.waiting_newsletter_message, admin_filter)
async def process_newsletter(message: types.Message, state: FSMContext):
    """Обработка текста рассылки и отправка всем пользователям"""
    newsletter_text = message.text
    
    if not newsletter_text:
        await message.answer("❌ Сообщение не может быть пустым")
        await state.clear()
        return
    
    # Показываем что начали рассылку
    progress_msg = await message.answer("🔄 Начинаю рассылку...")
    
    # Получаем всех уникальных пользователей из user_activity
    unique_users = await analytics_crud.get_unique_users()
    total_users = len(unique_users)
    
    if total_users == 0:
        await progress_msg.edit_text("❌ Нет пользователей для рассылки")
        await state.clear()
        return
    
    # Отправляем рассылку
    success_count = 0
    fail_count = 0
    
    for i, user_id in enumerate(unique_users, 1):
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>Новость от администратора:</b>\n\n{newsletter_text}",
                parse_mode="HTML"
            )
            success_count += 1
            
            # Обновляем прогресс каждые 10 сообщений
            if i % 10 == 0:
                await progress_msg.edit_text(
                    f"🔄 Рассылка... ({i}/{total_users})\n"
                    f"✅ Успешно: {success_count}\n"
                    f"❌ Ошибок: {fail_count}"
                )
            
            # Небольшая пауза чтобы не спамить
            await asyncio.sleep(0.1)
            
        except Exception as e:
            fail_count += 1
            logging.warning(f"Не удалось отправить пользователю {user_id}: {e}")
    
    # Финальный отчет
    await progress_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📊 Статистика:\n"
        f"• Всего пользователей: {total_users}\n"
        f"• ✅ Успешно: {success_count}\n"
        f"• ❌ Ошибок: {fail_count}\n"
        f"• 📈 Доставлено: {(success_count/total_users)*100:.1f}%",
        parse_mode="HTML"
    )
    
    await state.clear()