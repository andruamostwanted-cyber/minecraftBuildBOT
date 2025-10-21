from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


Base = declarative_base()

class BuildType(enum.Enum):
    SURVIVAL = "survival"
    ADVENTURE = "adventure" 
    HARDCORE = "hardcore"
    PUZZLE = "puzzle"
    CREATIVE = "creative"
    MINIGAME = "minigame"

class BuildStyle(enum.Enum):
    FANTASY = "fantasy"
    MEDIEVAL = "medieval"
    POSTAPOCALYPTIC = "postapocalyptic"
    SCI_FI = "scifi"
    MODERN = "modern"
    FAIRYTALE = "fairytale"

class Difficulty(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Telegram user ID
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связь с сборкой
    build = relationship("Build", back_populates="votes")

# Обновляем модель Build - добавляем связь с голосами и вычисляемые поля
class Build(Base):
    __tablename__ = "builds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    download_url = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)
    
    # Основные фильтры
    build_type = Column(Enum(BuildType), nullable=False)
    style = Column(Enum(BuildStyle), nullable=False)
    difficulty = Column(Enum(Difficulty), nullable=False)
    
    # Статистика
    downloads_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)  # Средний рейтинг (1-5)
    votes_count = Column(Integer, default=0)  # Количество оценок
    
    # Модерация
    is_approved = Column(Boolean, default=True)
    added_by = Column(Integer, nullable=True)  # Telegram user ID
    
    # Связь с голосами
    votes = relationship("Vote", back_populates="build", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Конвертирует объект в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'download_url': self.download_url,
            'image_url': self.image_url,
            'build_type': self.build_type.value,
            'style': self.style.value,
            'difficulty': self.difficulty.value,
            'downloads_count': self.downloads_count,
            'rating': self.rating,
            'votes_count': self.votes_count
        }
    
    @property
    def stars_display(self):
        """Возвращает строку со звездами для отображения"""
        full_stars = self.rating
        empty_stars = 5 - full_stars
        return "⭐" * full_stars + "☆" * empty_stars


BUILD_TYPE_MAP = {
    'survival': BuildType.SURVIVAL,
    'adventure': BuildType.ADVENTURE,
    'hardcore': BuildType.HARDCORE,
    'puzzle': BuildType.PUZZLE,
    'creative': BuildType.CREATIVE,
    'minigame': BuildType.MINIGAME
}

STYLE_MAP = {
    'fantasy': BuildStyle.FANTASY,
    'medieval': BuildStyle.MEDIEVAL,
    'postapocalyptic': BuildStyle.POSTAPOCALYPTIC,
    'scifi': BuildStyle.SCI_FI,
    'modern': BuildStyle.MODERN,
    'fairytale': BuildStyle.FAIRYTALE
}

DIFFICULTY_MAP = {
    'beginner': Difficulty.BEGINNER,
    'intermediate': Difficulty.INTERMEDIATE,
    'expert': Difficulty.EXPERT
}


class UserActivity(Base):
    __tablename__ = "user_activity"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    action = Column(String(50), nullable=False)  # start, random_build, filters, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)  # Дополнительная информация

class BotStats(Base):
    __tablename__ = "bot_stats"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_actions = Column(Integer, default=0)


class BuildShowcase(Base):
    __tablename__ = "build_showcase"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class BuildLike(Base):
    __tablename__ = "build_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    build_id = Column(Integer, ForeignKey('build_showcase.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)