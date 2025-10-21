import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import (
    get_main_keyboard,
    get_filters_keyboard,
    get_build_types_keyboard,
    get_style_keyboard,
    get_difficulty_keyboard,
    get_search_results_keyboard,
    get_rating_keyboard,
    get_rating_stats_keyboard,
    get_cancel_keyboard,
    get_showcase_keyboard
)

from filters import UserFilters

from db.crud import build_crud, analytics_crud
from db.models import BuildType, BuildStyle, Difficulty, BUILD_TYPE_MAP, STYLE_MAP, DIFFICULTY_MAP
from db.crud import showcase_crud


# Создаем роутер
router = Router()

class FilterStates(StatesGroup):
    waiting_for_filters = State()

class ShowcaseStates(StatesGroup):
    waiting_showcase_image = State()
    waiting_showcase_description = State()

# Создаем роутер
router = Router()

# Основные обработчики команд
@router.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
   
    # Логируем активность
    await analytics_crud.log_user_activity(
        user_id=message.from_user.id,
        action='start',
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    # Получаем количество сборок в базе
    builds_count = await build_crud.get_builds_count()
    
    welcome_text = f"""
🎮 <b>Добро пожаловать в Minecraft Build Bot!</b>

📊 <b>В нашей базе:</b> {builds_count} сборок

Я помогу тебе найти идеальную сборку для игры:

🎲 <b>Случайная сборка</b> - если не знаешь, что хочешь
🔍 <b>Подбор по фильтрам</b> - найду именно то, что нужно
➕ <b>Добавить сборку</b> - поделись своей сборкой

Выбери действие ниже 👇
    """
    
    await message.answer(
        welcome_text, 
        reply_markup=get_main_keyboard(), 
        parse_mode="HTML"
    )

@router.message(Command("random_build"))
async def random_build_handler(message: types.Message):
    """Обработчик команды /random_build"""
    await show_random_build(message)
    
    #logging user
    await analytics_crud.log_user_activity(
        user_id=message.from_user.id,
        action='random_build'
    )

@router.message(Command("build_filters"))
async def build_filters_handler(message: types.Message):
    """Обработчик команды /build_filters"""
    await show_filters_menu(message)

    #logging user
    await analytics_crud.log_user_activity(
        user_id=message.from_user.id,
        action='build_filters'
    )

# Обработчики для текстовых кнопок
@router.message(lambda message: message.text == "🎲 Случайная сборка")
async def random_build_button_handler(message: types.Message):
    await show_random_build(message)

    #logging user
    await analytics_crud.log_user_activity(
        user_id=message.from_user.id,
        action='random_build'
    )

@router.message(lambda message: message.text == "🔍 Подбор по фильтрам")
async def filters_button_handler(message: types.Message):
    await show_filters_menu(message)

    #logging user
    await analytics_crud.log_user_activity(
        user_id=message.from_user.id,
        action='build_filters'
    )

@router.message(lambda message: message.text == "➕ Добавить сборку")
async def add_build_button_handler(message: types.Message):
    await message.answer(
        "📝 <b>Добавление сборки</b>\n\n"
        "Эта функция скоро будет доступна! 🚀\n"
        "Следи за обновлениями.",
        parse_mode="HTML"
    )

@router.message(lambda message: message.text == "📊 Топ сборок")
async def top_builds_button_handler(message: types.Message):
    await show_top_builds(message)

# CALLBACK ОБРАБОТЧИКИ ДЛЯ ФИЛЬТРОВ

@router.callback_query(F.data == "filter_type")
async def filter_type_callback(callback: types.CallbackQuery):
    """Обработчик выбора типа сборки"""
    await callback.message.edit_text(
        "🎯 <b>Выбери тип сборки:</b>\n\n"
        "Какой игровой опыт ты ищешь?",
        reply_markup=get_build_types_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "filter_style")
async def filter_style_callback(callback: types.CallbackQuery):
    """Обработчик выбора стиля"""
    await callback.message.edit_text(
        "🏰 <b>Выбери стиль сборки:</b>\n\n"
        "В каком сеттинге хочешь играть?",
        reply_markup=get_style_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "filter_difficulty")
async def filter_difficulty_callback(callback: types.CallbackQuery):
    """Обработчик выбора сложности"""
    await callback.message.edit_text(
        "⚡ <b>Выбери сложность:</b>\n\n"
        "Насколько сложную сборку ты ищешь?",
        reply_markup=get_difficulty_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("type_"))
async def build_type_selected_callback(callback: types.CallbackQuery):
    """Обработчик выбора конкретного типа"""
    build_type_key = callback.data.replace("type_", "")
    build_type_enum = BUILD_TYPE_MAP.get(build_type_key)
    
    if build_type_enum:
        UserFilters.set_filter(callback.from_user.id, 'build_type', build_type_key)
        
        await callback.message.edit_text(
            f"✅ <b>Тип сборки выбран!</b>\n\n"
            f"{UserFilters.get_active_filters_text(callback.from_user.id)}\n\n"
            f"Продолжи выбор фильтров:",
            reply_markup=get_filters_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("Тип сборки сохранен! ✅")
    else:
        await callback.answer("❌ Ошибка выбора типа", show_alert=True)

@router.callback_query(F.data.startswith("style_"))
async def style_selected_callback(callback: types.CallbackQuery):
    """Обработчик выбора конкретного стиля"""
    style_key = callback.data.replace("style_", "")
    style_enum = STYLE_MAP.get(style_key)
    
    if style_enum:
        UserFilters.set_filter(callback.from_user.id, 'style', style_key)
        
        await callback.message.edit_text(
            f"✅ <b>Стиль выбран!</b>\n\n"
            f"{UserFilters.get_active_filters_text(callback.from_user.id)}\n\n"
            f"Продолжи выбор фильтров:",
            reply_markup=get_filters_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("Стиль сохранен! ✅")
    else:
        await callback.answer("❌ Ошибка выбора стиля", show_alert=True)

@router.callback_query(F.data.startswith("difficulty_"))
async def difficulty_selected_callback(callback: types.CallbackQuery):
    """Обработчик выбора сложности"""
    difficulty_key = callback.data.replace("difficulty_", "")
    difficulty_enum = DIFFICULTY_MAP.get(difficulty_key)
    
    if difficulty_enum:
        UserFilters.set_filter(callback.from_user.id, 'difficulty', difficulty_key)
        
        await callback.message.edit_text(
            f"✅ <b>Сложность выбрана!</b>\n\n"
            f"{UserFilters.get_active_filters_text(callback.from_user.id)}\n\n"
            f"Продолжи выбор фильтров:",
            reply_markup=get_filters_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("Сложность сохранена! ✅")
    else:
        await callback.answer("❌ Ошибка выбора сложности", show_alert=True)

@router.callback_query(F.data == "back_to_filters")
async def back_to_filters_callback(callback: types.CallbackQuery):
    """Обработчик возврата к фильтрам"""
    await callback.message.edit_text(
        f"🔍 <b>Подбор сборки по фильтрам</b>\n\n"
        f"{UserFilters.get_active_filters_text(callback.from_user.id)}\n\n"
        f"Выбери параметры для поиска:",
        reply_markup=get_filters_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "filter_search")
async def filter_search_callback(callback: types.CallbackQuery):
    """Обработчик поиска по фильтрам"""
    filters = UserFilters.get_filters(callback.from_user.id)
    
    # Проверяем, выбраны ли фильтры
    if not any(filters.values()):
        await callback.answer("❌ Сначала выбери хотя бы один фильтр!", show_alert=True)
        return
    
    # Преобразуем фильтры в enum'ы для БД
    build_type_enum = BUILD_TYPE_MAP.get(filters['build_type']) if filters['build_type'] else None
    style_enum = STYLE_MAP.get(filters['style']) if filters['style'] else None
    difficulty_enum = DIFFICULTY_MAP.get(filters['difficulty']) if filters['difficulty'] else None
    
    # Ищем сборки в БД
    builds = await build_crud.get_builds_by_filters(
        build_type=build_type_enum,
        style=style_enum,
        difficulty=difficulty_enum,
        limit=5
    )
    
    if not builds:
        await callback.message.edit_text(
            f"❌ <b>По вашему запросу ничего не найдено</b>\n\n"
            f"{UserFilters.get_active_filters_text(callback.from_user.id)}\n\n"
            f"Попробуйте изменить фильтры или посмотреть случайную сборку.",
            reply_markup=get_filters_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Показываем первую найденную сборку - редактируем текущее сообщение
    build = builds[0]
    await handle_callback_build(callback, build)
    await callback.answer()

async def handle_callback_build(callback: types.CallbackQuery, build):
    """Обработка callback'а с показом сборки - всегда отправляет новое сообщение"""
    text = format_build_text(build)
    
    # Сначала пытаемся удалить старое сообщение
    try:
        await callback.message.delete()
    except Exception as e:
        logging.warning(f"Не удалось удалить старое сообщение: {e}")
    
    # Отправляем новое сообщение
    if build.image_url:
        try:
            await callback.message.answer_photo(
                photo=build.image_url,
                caption=text,
                reply_markup=get_search_results_keyboard(build.id),
                parse_mode="HTML"
            )
            return
        except Exception as e:
            logging.warning(f"Не удалось отправить фото, используем текст: {e}")
    
    # Текстовый вариант
    await callback.message.answer(
        text,
        reply_markup=get_search_results_keyboard(build.id),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@router.callback_query(F.data == "random_another")
async def random_another_callback(callback: types.CallbackQuery):
    """Обработчик для другой случайной сборки"""
    try:
        logging.info(f"🔄 Пользователь {callback.from_user.id} запросил другую случайную сборку")
        
        build = await build_crud.get_random_build()
        if build:
            logging.info(f"✅ Найдена сборка: {build.name} (ID: {build.id})")
            await handle_callback_build(callback, build)  # Используем новую функцию
        else:
            logging.warning("❌ В базе нет сборок или они не одобрены")
            await callback.message.edit_text(
                "❌ <b>В базе пока нет сборок</b>\n\n",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f"🚨 Ошибка в random_another_callback: {e}", exc_info=True)
        await callback.message.answer(
            "❌ <b>Произошла ошибка при поиске сборки</b>\n\n"
            "Попробуйте еще раз позже.",
            parse_mode="HTML"
        )
    await callback.answer()




@router.callback_query(F.data == "new_search")
async def new_search_callback(callback: types.CallbackQuery):
    """Обработчик нового поиска"""
    UserFilters.clear_filters(callback.from_user.id)
    await show_filters_menu(callback.message)
    await callback.answer()

@router.callback_query(F.data.startswith("download_"))
async def download_build_callback(callback: types.CallbackQuery):
    """Обработчик скачивания сборки - увеличивает счетчик"""
    try:
        # Извлекаем ID сборки из callback data
        build_id_str = callback.data.replace("download_", "")
        
        if build_id_str.isdigit():
            build_id = int(build_id_str)
            build = await build_crud.get_build_by_id(build_id=build_id)
            
            # Увеличиваем счетчик скачиваний
            updated_build = await build_crud.increment_downloads(build_id)
            
            if updated_build:
                # Обновляем сообщение с новым счетчиком
                await handle_callback_build(callback, updated_build)
                await callback.answer(f"📥 Ссылка отображена")
                await callback.message.answer(text=f"📥 <a href='{build.download_url}'>Скачать</a>")
            else:
                await callback.answer("❌ Сборка не найдена", show_alert=True)
        else:
            # Резервный вариант для старых сообщений без ID
            await callback.answer(f"📥 Ссылка отображена")
            
    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logging.error(f"Error incrementing download count: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        await callback.answer("❌ Ошибка при обновлении счетчика", show_alert=True)

@router.callback_query(F.data == "download_build")
async def download_build_fallback_callback(callback: types.CallbackQuery):
    """Резервный обработчик для старых сообщений без ID в callback"""
    await callback.answer("📥 Ссылка для скачивания в сообщении выше!", show_alert=True)

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

async def send_new_build_message(message: types.Message, build):
    """Отправить новое сообщение с информацией о сборке"""
    text = format_build_text(build)
    
    # Если есть изображение, отправляем как фото с описанием
    if build.image_url:
        try:
            await message.answer_photo(
                photo=build.image_url,
                caption=text,
                reply_markup=get_search_results_keyboard(build_id=build.id),
                parse_mode="HTML"
            )
            return
        except Exception as e:
            logging.error(f"Error sending photo, falling back to text: {e}")
    
    # Fallback - обычное текстовое сообщение
    await message.answer(
        text,
        reply_markup=get_search_results_keyboard(build.id),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

async def edit_build_message(message: types.Message, build):
    """Отредактировать сообщение с информацией о сборке"""
    text = format_build_text(build)
    
    await message.edit_text(
        text,
        reply_markup=get_search_results_keyboard(build.id),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    # ОБЩАЯ ФУНКЦИЯ ДЛЯ ФОРМАТИРОВАНИЯ ТЕКСТА
def format_build_text(build):
    """Форматировать текст сборки"""
    type_display = {
        BuildType.SURVIVAL: "🏕️ Выживание",
        BuildType.ADVENTURE: "🗺️ Приключение/РПГ",
        BuildType.HARDCORE: "💀 Хардкор", 
        BuildType.PUZZLE: "🧩 Пазл/Головоломка",
        BuildType.CREATIVE: "🎨 Творчество",
        BuildType.MINIGAME: "🎯 Мини-игры"
    }.get(build.build_type, build.build_type.value)
    
    style_display = {
        BuildStyle.FANTASY: "🧙‍♂️ Фэнтези",
        BuildStyle.MEDIEVAL: "🏰 Средневековье",
        BuildStyle.POSTAPOCALYPTIC: "☢️ Постапокалипсис",
        BuildStyle.SCI_FI: "🚀 Техно/Научная фантастика", 
        BuildStyle.MODERN: "🏙️ Современный мир",
        BuildStyle.FAIRYTALE: "🌈 Сказочный/Мультяшный"
    }.get(build.style, build.style.value)
    
    difficulty_display = {
        Difficulty.BEGINNER: "🟢 Для новичков",
        Difficulty.INTERMEDIATE: "🟡 Средняя",
        Difficulty.EXPERT: "🔴 Для экспертов"
    }.get(build.difficulty, build.difficulty.value)
    
    # Добавляем отображение рейтинга
    rating_display = f"⭐ {build.rating}/5" if build.rating > 0 else "☆ Еще нет оценок"
    
    return (
        f"🎲 <b>{build.name}</b>\n\n"
        f"{build.description}\n\n"
        f"🔹 <b>Тип:</b> {type_display}\n"
        f"🔹 <b>Стиль:</b> {style_display}\n" 
        f"🔹 <b>Сложность:</b> {difficulty_display}\n"
        f"🔹 <b>Скачиваний:</b> {build.downloads_count}\n"
        f"🔹 <b>Рейтинг:</b> {rating_display} ({build.votes_count} оценок)\n"
        f"🔹 <b>ID сборки:</b> {build.id}\n\n"
    )


async def show_build_details(message: types.Message, build, similar_builds=None):
    """Показать детали сборки (отправляет новое сообщение)"""
    # Форматируем тип, стиль и сложность для красивого отображения
    type_display = {
        BuildType.SURVIVAL: "🏕️ Выживание",
        BuildType.ADVENTURE: "🗺️ Приключение/РПГ",
        BuildType.HARDCORE: "💀 Хардкор", 
        BuildType.PUZZLE: "🧩 Пазл/Головоломка",
        BuildType.CREATIVE: "🎨 Творчество",
        BuildType.MINIGAME: "🎯 Мини-игры"
    }.get(build.build_type, build.build_type.value)
    
    style_display = {
        BuildStyle.FANTASY: "🧙‍♂️ Фэнтези",
        BuildStyle.MEDIEVAL: "🏰 Средневековье",
        BuildStyle.POSTAPOCALYPTIC: "☢️ Постапокалипсис",
        BuildStyle.SCI_FI: "🚀 Техно/Научная фантастика", 
        BuildStyle.MODERN: "🏙️ Современный мир",
        BuildStyle.FAIRYTALE: "🌈 Сказочный/Мультяшный"
    }.get(build.style, build.style.value)
    
    difficulty_display = {
        Difficulty.BEGINNER: "🟢 Для новичков",
        Difficulty.INTERMEDIATE: "🟡 Средняя",
        Difficulty.EXPERT: "🔴 Для экспертов"
    }.get(build.difficulty, build.difficulty.value)
    
    text = (
        f"🎲 <b>{build.name}</b>\n\n"
        f"{build.description}\n\n"
        f"🔹 <b>Тип:</b> {type_display}\n"
        f"🔹 <b>Стиль:</b> {style_display}\n" 
        f"🔹 <b>Сложность:</b> {difficulty_display}\n"
        f"🔹 <b>Скачиваний:</b> {build.downloads_count}\n\n"
    )
    
    # Всегда отправляем новое сообщение
    await message.answer(
        text,
        reply_markup=get_search_results_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

async def show_random_build(message: types.Message):
    """Показать случайную сборку из БД (для reply-кнопок)"""
    try:
        build = await build_crud.get_random_build()
        if build:
            # Для reply-кнопок отправляем новое сообщение
            await send_new_build_message(message, build)
        else:
            await message.answer(
                "❌ <b>В базе пока нет сборок</b>\n\n"
                "Попробуйте позже или добавьте свои сборки.",
                parse_mode="HTML"
            )
    except Exception as e:
        await message.answer(
            "❌ <b>Произошла ошибка при поиске сборки</b>\n\n"
            "Попробуйте еще раз позже.",
            parse_mode="HTML"
        )

async def show_filters_menu(message: types.Message):
    """Показать меню фильтров"""
    user_id = message.from_user.id
    await message.answer(
        f"🔍 <b>Подбор сборки по фильтрам</b>\n\n"
        f"{UserFilters.get_active_filters_text(user_id)}\n\n"
        f"Выбери параметры для поиска идеальной сборки:",
        reply_markup=get_filters_keyboard(),
        parse_mode="HTML"
    )

async def show_top_builds(message: types.Message):
    """Показать топ сборок"""
    top_builds = await build_crud.get_top_builds(limit=5)
    
    if not top_builds:
        await message.answer(
            "🏆 <b>Топ сборок</b>\n\n"
            "Пока нет данных о популярных сборках.",
            parse_mode="HTML"
        )
        return
    
    text = "🏆 <b>Топ-5 самых популярных сборок:</b>\n\n"
    
    for i, build in enumerate(top_builds, 1):
        text += (
            f"{i}. <b>{build.name}</b>\n"
            f"   📥 Скачиваний: {build.downloads_count}\n"
            f"   ⭐ Рейтинг: {build.rating}/5\n\n"
        )
    
    text += "Используйте поиск по фильтрам чтобы найти эти сборки! 🔍"
    
    await message.answer(text, parse_mode="HTML")
    print(message.from_user.id)

@router.callback_query(F.data.startswith("rate_"))
async def rate_build_callback(callback: types.CallbackQuery):
    """Обработчик оценки сборки"""
    try:
        # Извлекаем данные из callback
        parts = callback.data.split("_")
        build_id = int(parts[1])
        rating = int(parts[2])
        
        if rating == 0:
            # Показываем клавиатуру для оценки
            user_vote = await build_crud.get_user_vote(build_id, callback.from_user.id)
            user_rating = user_vote.rating if user_vote else None
            
            await callback.message.edit_reply_markup(
                reply_markup=get_rating_keyboard(build_id, user_rating)
            )
            await callback.answer("Выберите оценку от 1 до 5 звезд")
            return
        
        # Проверяем валидность оценки
        if rating < 1 or rating > 5:
            await callback.answer("❌ Оценка должна быть от 1 до 5 звезд", show_alert=True)
            return
        
        # Добавляем оценку
        result = await build_crud.add_vote(build_id, callback.from_user.id, rating)
        
        if result['success']:
            # Обновляем сообщение с новым рейтингом
            build = await build_crud.get_build_by_id(build_id)
            await edit_build_message(callback.message, build)
            await callback.answer(f"✅ Спасибо за оценку! Вы поставили {rating}⭐")
        else:
            if result['error'] == 'already_voted':
                await callback.answer("❌ Вы уже оценили эту сборку!", show_alert=True)
            else:
                await callback.answer("❌ Ошибка при оценке сборки", show_alert=True)
                
    except Exception as e:
        logging.error(f"Error rating build: {e}")
        await callback.answer("❌ Ошибка при оценке сборки", show_alert=True)

@router.callback_query(F.data.startswith("rating_stats_"))
async def rating_stats_callback(callback: types.CallbackQuery):
    """Обработчик просмотра статистики рейтинга"""
    try:
        build_id = int(callback.data.replace("rating_stats_", ""))
        stats = await build_crud.get_build_rating_stats(build_id)
        
        if not stats:
            await callback.answer("❌ Статистика не найдена", show_alert=True)
            return
        
        # Формируем текст статистики
        stats_text = f"📊 <b>Статистика рейтинга</b>\n\n"
        stats_text += f"⭐ Средний рейтинг: <b>{stats['average_rating']}/5</b>\n"
        stats_text += f"👥 Всего оценок: <b>{stats['votes_count']}</b>\n\n"
        
        # Распределение оценок
        if stats['distribution']:
            stats_text += "<b>Распределение оценок:</b>\n"
            for star in range(5, 0, -1):
                count = stats['distribution'].get(star, 0)
                percentage = (count / stats['votes_count']) * 100 if stats['votes_count'] > 0 else 0
                bar = "█" * int(percentage / 10)  # Простая визуализация
                stats_text += f"{'⭐' * star}{'☆' * (5-star)}: {count} {bar} ({percentage:.1f}%)\n"
        
        #удаляем старое сообщение, если возможно
        try:
            await callback.message.delete()
        except Exception as e:
            logging.warning(f"Не удалось удалить старое сообщение: {e}")

        await callback.message.answer(
            stats_text,
            reply_markup=get_rating_stats_keyboard(build_id),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Error showing rating stats: {e}")
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)

@router.callback_query(F.data.startswith("back_to_build_"))
async def back_to_build_callback(callback: types.CallbackQuery):
    """Обработчик возврата к сборке из статистики"""
    try:
        build_id = int(callback.data.replace("back_to_build_", ""))
        build = await build_crud.get_build_by_id(build_id)
        
        if build:
            await handle_callback_build(callback, build)
        else:
            await callback.answer("❌ Сборка не найдена", show_alert=True)
            
    except Exception as e:
        logging.error(f"Error returning to build: {e}")
        await callback.answer("❌ Ошибка при возврате к сборке", show_alert=True)

# Команда для просмотра построек
@router.message(F.text == "🏗️ Показать постройки")
async def showcase_handler(message: types.Message):
    """Показать случайную постройку"""
    build = await showcase_crud.get_random_showcase()
    
    if not build:
        keyboard = [
            [types.InlineKeyboardButton(text="📤 Добавить первую постройку", callback_data="add_showcase")]
        ]
        reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)

        await message.answer(
            "🏗️ <b>Пока нет построек</b>\n\n"
            "Будь первым - добавь свою крутую постройку!",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        return
    
    text = f"🏗️ <b>Постройка от пользователя</b>\n"
    if build.description:
        text += f"\n{build.description}\n"
    text += f"\n❤️ <b>Лайков:</b> {build.likes_count}"
    
    await message.answer_photo(
        photo=build.image_url,
        caption=text,
        reply_markup=get_showcase_keyboard(build.id)
    )

# Callback для лайка
@router.callback_query(F.data.startswith("like_build_"))
async def like_build_callback(callback: types.CallbackQuery):
    """Обработчик лайка постройки"""
    build_id = int(callback.data.replace("like_build_", ""))
    
    success = await showcase_crud.like_build(build_id, callback.from_user.id)
    
    if success:
        await callback.answer("❤️ Лайк поставлен!")
    else:
        await callback.answer("❌ Вы уже лайкали эту постройку")

# Callback для следующей постройки
@router.callback_query(F.data == "next_showcase")
async def next_showcase_callback(callback: types.CallbackQuery):
    """Показать следующую постройку"""
    build = await showcase_crud.get_random_showcase()
    
    if build:
        text = f"🏗️ <b>Постройка от пользователя</b>\n"
        if build.description:
            text += f"\n{build.description}\n"
        text += f"\n❤️ <b>Лайков:</b> {build.likes_count}"
        
        await callback.message.answer_photo(photo=build.image_url, caption=text, parse_mode="HTML", reply_markup=get_showcase_keyboard(build.id))
        
    else:
        await callback.answer("❌ Больше построек нет")
    
    await callback.answer()

# Начало добавления постройки
@router.callback_query(F.data == "add_showcase")
async def add_showcase_start(callback: types.CallbackQuery, state: FSMContext):
    """Начать процесс добавления постройки"""
    await callback.message.answer(
        "🏗️ <b>Добавление постройки</b>\n\n"
        "Отправь ссылку на изображение твоей постройки:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ShowcaseStates.waiting_showcase_image)
    await callback.answer()

# Обработчик изображения
@router.message(ShowcaseStates.waiting_showcase_image)
async def process_showcase_image(message: types.Message, state: FSMContext):
    """Обработка изображения постройки"""
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено", reply_markup=get_main_keyboard())
        return
    
    if not message.text.startswith(('http://', 'https://')):
        await message.answer("❌ Это не ссылка! Отправь прямую ссылку на изображение")
        return
    
    await state.update_data(image_url=message.text)
    await message.answer(
        "📝 Теперь добавь описание (или отправь 'пропустить'):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ShowcaseStates.waiting_showcase_description)

# Обработчик описания
@router.message(ShowcaseStates.waiting_showcase_description)
async def process_showcase_description(message: types.Message, state: FSMContext):
    """Обработка описания постройки"""
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено", reply_markup=get_main_keyboard())
        return
    
    user_data = await state.get_data()
    description = None if message.text.lower() == "пропустить" else message.text
    
    # Сохраняем постройку
    build = await showcase_crud.add_build_showcase(
        user_id=message.from_user.id,
        image_url=user_data['image_url'],
        description=description
    )
    
    await message.answer(
        "✅ <b>Постройка добавлена!</b>\n\n"
        "Теперь другие пользователи смогут её оценить ❤️",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML",
    )
    await state.clear()