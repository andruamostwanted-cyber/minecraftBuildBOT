user_filters = {}

class UserFilters:
    """Класс для управления фильтрами пользователя"""
    
    @staticmethod
    def get_filters(user_id: int):
        """Получить фильтры пользователя"""
        return user_filters.get(user_id, {
            'build_type': None,
            'style': None,
            'difficulty': None
        })
    
    @staticmethod
    def set_filter(user_id: int, filter_type: str, value: str):
        """Установить фильтр пользователя"""
        if user_id not in user_filters:
            user_filters[user_id] = {
                'build_type': None,
                'style': None,
                'difficulty': None
            }
        user_filters[user_id][filter_type] = value
    
    @staticmethod
    def clear_filters(user_id: int):
        """Очистить фильтры пользователя"""
        if user_id in user_filters:
            user_filters[user_id] = {
                'build_type': None,
                'style': None,
                'difficulty': None
            }
    
    @staticmethod
    def get_active_filters_text(user_id: int):
        """Получить текст с активными фильтрами"""
        filters = UserFilters.get_filters(user_id)
        active_filters = []
        
        if filters['build_type']:
            build_types = {
                'survival': '🏕️ Выживание',
                'adventure': '🗺️ Приключение/РПГ', 
                'hardcore': '💀 Хардкор',
                'puzzle': '🧩 Пазл/Головоломка',
                'creative': '🎨 Творчество',
                'minigame': '🎯 Мини-игры'
            }
            active_filters.append(f"Тип: {build_types[filters['build_type']]}")
        
        if filters['style']:
            styles = {
                'fantasy': '🧙‍♂️ Фэнтези',
                'medieval': '🏰 Средневековье',
                'postapocalyptic': '☢️ Постапокалипсис',
                'scifi': '🚀 Техно/Научная фантастика',
                'modern': '🏙️ Современный мир',
                'fairytale': '🌈 Сказочный/Мультяшный'
            }
            active_filters.append(f"Стиль: {styles[filters['style']]}")
            
        if filters['difficulty']:
            difficulties = {
                'beginner': '🟢 Для новичков',
                'intermediate': '🟡 Средняя', 
                'expert': '🔴 Для экспертов'
            }
            active_filters.append(f"Сложность: {difficulties[filters['difficulty']]}")
        
        if not active_filters:
            return "❌ Фильтры не выбраны"
        
        return "✅ " + " | ".join(active_filters)