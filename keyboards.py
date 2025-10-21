from aiogram import types

def get_main_keyboard():
    """Основная клавиатура меню"""
    keyboard = [
        [types.KeyboardButton(text="🎲 Случайная сборка"), types.KeyboardButton(text="🔍 Подбор по фильтрам")],
        [types.KeyboardButton(text="🏗️ Показать постройки"), types.KeyboardButton(text="📊 Топ сборок")],
        [types.KeyboardButton(text="📞 Связаться с нами")]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

def get_contact_cancel_keyboard():
    """Клавиатура для отмены отправки сообщения"""
    keyboard = [
        [types.KeyboardButton(text="❌ Отменить отправку")]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_filters_keyboard():
    """Клавиатура для фильтров"""
    keyboard = [
        [types.InlineKeyboardButton(text="🎯 Тип сборки", callback_data="filter_type")],
        [types.InlineKeyboardButton(text="🏰 Стиль", callback_data="filter_style")],
        [types.InlineKeyboardButton(text="⚡ Сложность", callback_data="filter_difficulty")],
        [types.InlineKeyboardButton(text="🔍 Начать поиск", callback_data="filter_search")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_build_types_keyboard():
    """Клавиатура для выбора типа сборки"""
    keyboard = [
        [types.InlineKeyboardButton(text="🏕️ Выживание", callback_data="type_survival")],
        [types.InlineKeyboardButton(text="🗺️ Приключение/РПГ", callback_data="type_adventure")],
        [types.InlineKeyboardButton(text="💀 Хардкор", callback_data="type_hardcore")],
        [types.InlineKeyboardButton(text="🧩 Пазл/Головоломка", callback_data="type_puzzle")],
        [types.InlineKeyboardButton(text="🎨 Творчество", callback_data="type_creative")],
        [types.InlineKeyboardButton(text="🎯 Мини-игры", callback_data="type_minigame")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_style_keyboard():
    """Клавиатура для выбора стиля"""
    keyboard = [
        [types.InlineKeyboardButton(text="🧙‍♂️ Фэнтези", callback_data="style_fantasy")],
        [types.InlineKeyboardButton(text="🏰 Средневековье", callback_data="style_medieval")],
        [types.InlineKeyboardButton(text="☢️ Постапокалипсис", callback_data="style_postapocalyptic")],
        [types.InlineKeyboardButton(text="🚀 Техно/Научная фантастика", callback_data="style_scifi")],
        [types.InlineKeyboardButton(text="🏙️ Современный мир", callback_data="style_modern")],
        [types.InlineKeyboardButton(text="🌈 Сказочный/Мультяшный", callback_data="style_fairytale")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_difficulty_keyboard():
    """Клавиатура для выбора сложности"""
    keyboard = [
        [types.InlineKeyboardButton(text="🟢 Для новичков", callback_data="difficulty_beginner")],
        [types.InlineKeyboardButton(text="🟡 Средняя", callback_data="difficulty_intermediate")],
        [types.InlineKeyboardButton(text="🔴 Для экспертов", callback_data="difficulty_expert")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_build_types_keyboard():
    """Клавиатура для выбора типа сборки"""
    keyboard = [
        [types.InlineKeyboardButton(text="🏕️ Выживание", callback_data="type_survival")],
        [types.InlineKeyboardButton(text="🗺️ Приключение/РПГ", callback_data="type_adventure")],
        [types.InlineKeyboardButton(text="💀 Хардкор", callback_data="type_hardcore")],
        [types.InlineKeyboardButton(text="🧩 Пазл/Головоломка", callback_data="type_puzzle")],
        [types.InlineKeyboardButton(text="🎨 Творчество", callback_data="type_creative")],
        [types.InlineKeyboardButton(text="🎯 Мини-игры", callback_data="type_minigame")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_style_keyboard():
    """Клавиатура для выбора стиля"""
    keyboard = [
        [types.InlineKeyboardButton(text="🧙‍♂️ Фэнтези", callback_data="style_fantasy")],
        [types.InlineKeyboardButton(text="🏰 Средневековье", callback_data="style_medieval")],
        [types.InlineKeyboardButton(text="☢️ Постапокалипсис", callback_data="style_postapocalyptic")],
        [types.InlineKeyboardButton(text="🚀 Техно/Научная фантастика", callback_data="style_scifi")],
        [types.InlineKeyboardButton(text="🏙️ Современный мир", callback_data="style_modern")],
        [types.InlineKeyboardButton(text="🌈 Сказочный/Мультяшный", callback_data="style_fairytale")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_difficulty_keyboard():
    """Клавиатура для выбора сложности"""
    keyboard = [
        [types.InlineKeyboardButton(text="🟢 Для новичков", callback_data="difficulty_beginner")],
        [types.InlineKeyboardButton(text="🟡 Средняя", callback_data="difficulty_intermediate")],
        [types.InlineKeyboardButton(text="🔴 Для экспертов", callback_data="difficulty_expert")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_search_results_keyboard(build_id: int = None):
    """Клавиатура для результатов поиска"""
    keyboard = []
    
    # Кнопки основного действия
    if build_id:
        keyboard.extend([
            [types.InlineKeyboardButton(text="📥 Скачать", callback_data=f"download_{build_id}")],
            [types.InlineKeyboardButton(text="⭐ Оценить сборку", callback_data=f"rate_{build_id}_0")],
            [types.InlineKeyboardButton(text="📊 Статистика рейтинга", callback_data=f"rating_stats_{build_id}")],
            [types.InlineKeyboardButton(text="🎲 Другая случайная", callback_data="random_another")],
            [types.InlineKeyboardButton(text="🔍 Новый поиск", callback_data="new_search")],
        ])
    else:
        keyboard.extend([
            [types.InlineKeyboardButton(text="📥 Скачать", callback_data="download_build")],
            [types.InlineKeyboardButton(text="🎲 Другая случайная", callback_data="random_another")],
            [types.InlineKeyboardButton(text="🔍 Новый поиск", callback_data="new_search")],
        ])
        
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_keyboard():
    """Клавиатура админ-панели"""
    keyboard = [
        [types.KeyboardButton(text="🎺 Сделать рассылку")],
        [types.KeyboardButton(text="📊 Статистика")],
        [types.KeyboardButton(text="📦 Управление сборками")],
        [types.KeyboardButton(text="⏳ Модерация")],
        [types.KeyboardButton(text="🎮 Основное меню")]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

def get_admin_builds_keyboard():
    """Клавиатура управления сборками"""
    keyboard = [
        [types.KeyboardButton(text="👁️ Просмотр всех сборок"), types.KeyboardButton(text="📋 Список построек")],
        [types.KeyboardButton(text="➕ Добавить сборку (admin)")],
        [types.KeyboardButton(text="❌ Удалить сборку")],
        [types.KeyboardButton(text="⬅️ Назад в админку")]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Управление сборками..."
    )

def get_admin_moderation_keyboard():
    """Клавиатура модерации"""
    keyboard = [
        [types.KeyboardButton(text="👁️ Просмотр ожидающих")],
        [types.KeyboardButton(text="✅ Одобрить все")],
        [types.KeyboardButton(text="⬅️ Назад в админку")]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Модерация..."
    )

def get_admin_build_types_keyboard():
    """Клавиатура для выбора типа сборки (админка)"""
    keyboard = [
        [types.InlineKeyboardButton(text="🏕️ Выживание", callback_data="admin_type_survival")],
        [types.InlineKeyboardButton(text="🗺️ Приключение/РПГ", callback_data="admin_type_adventure")],
        [types.InlineKeyboardButton(text="💀 Хардкор", callback_data="admin_type_hardcore")],
        [types.InlineKeyboardButton(text="🧩 Пазл/Головоломка", callback_data="admin_type_puzzle")],
        [types.InlineKeyboardButton(text="🎨 Творчество", callback_data="admin_type_creative")],
        [types.InlineKeyboardButton(text="🎯 Мини-игры", callback_data="admin_type_minigame")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_style_keyboard():
    """Клавиатура для выбора стиля (админка)"""
    keyboard = [
        [types.InlineKeyboardButton(text="🧙‍♂️ Фэнтези", callback_data="admin_style_fantasy")],
        [types.InlineKeyboardButton(text="🏰 Средневековье", callback_data="admin_style_medieval")],
        [types.InlineKeyboardButton(text="☢️ Постапокалипсис", callback_data="admin_style_postapocalyptic")],
        [types.InlineKeyboardButton(text="🚀 Техно/Научная фантастика", callback_data="admin_style_scifi")],
        [types.InlineKeyboardButton(text="🏙️ Современный мир", callback_data="admin_style_modern")],
        [types.InlineKeyboardButton(text="🌈 Сказочный/Мультяшный", callback_data="admin_style_fairytale")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_difficulty_keyboard():
    """Клавиатура для выбора сложности (админка)"""
    keyboard = [
        [types.InlineKeyboardButton(text="🟢 Для новичков", callback_data="admin_difficulty_beginner")],
        [types.InlineKeyboardButton(text="🟡 Средняя", callback_data="admin_difficulty_intermediate")],
        [types.InlineKeyboardButton(text="🔴 Для экспертов", callback_data="admin_difficulty_expert")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_rating_keyboard(build_id: int, user_rating: int = None):
    """Клавиатура для оценки сборки"""
    keyboard = []
    
    # Создаем строку с звездами
    stars_row = []
    for i in range(1, 6):
        star_text = "⭐" if user_rating and i <= user_rating else "☆"
        stars_row.append(
            types.InlineKeyboardButton(
                text=f"{star_text} {i}", 
                callback_data=f"rate_{build_id}_{i}"
            )
        )
    
    keyboard.append(stars_row)
    
    # Кнопка для просмотра статистики
    keyboard.append([
        types.InlineKeyboardButton(
            text="📊 Статистика рейтинга", 
            callback_data=f"rating_stats_{build_id}"
        )
    ])
    
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_rating_stats_keyboard(build_id: int):
    """Клавиатура для статистики рейтинга"""
    keyboard = [
        [types.InlineKeyboardButton(text="⭐ Оценить сборку", callback_data=f"rate_{build_id}_0")],
        [types.InlineKeyboardButton(text="⬅️ Назад к сборке", callback_data=f"back_to_build_{build_id}")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_showcase_keyboard(build_id: int):
    """Клавиатура для показа построек"""
    keyboard = [
        [types.InlineKeyboardButton(text="❤️ Лайк", callback_data=f"like_build_{build_id}")],
        [types.InlineKeyboardButton(text="➡️ Дальше", callback_data="next_showcase")],
        [types.InlineKeyboardButton(text="📤 Добавить свою", callback_data="add_showcase")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_cancel_keyboard():
    """Клавиатура отмены"""
    keyboard = [
        [types.KeyboardButton(text="❌ Отменить")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)