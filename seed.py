import asyncio
from db.models import BuildType, BuildStyle, Difficulty
from db.crud import build_crud
from db.session import init_db

async def seed_database():
    """Наполнить базу тестовыми данными"""
    await init_db()
    
    test_builds = [
        {
            "name": "Magical Kingdom",
            "description": "Сборка в стиле фэнтези с магией, драконами и загадочными замками. Идеально для любителей волшебства и приключений.",
            "download_url": "https://www.curseforge.com/minecraft/modpacks/magical-kingdom",
            "build_type": BuildType.ADVENTURE,
            "style": BuildStyle.FANTASY,
            "difficulty": Difficulty.INTERMEDIATE,
            "image_url": "https://example.com/image1.jpg"
        },
        {
            "name": "Tech Revolution", 
            "description": "Погрузись в мир высоких технологий с автоматизацией, роботами и сложными механизмами. Для любителей технического прогресса.",
            "download_url": "https://www.curseforge.com/minecraft/modpacks/tech-revolution",
            "build_type": BuildType.SURVIVAL,
            "style": BuildStyle.SCI_FI,
            "difficulty": Difficulty.EXPERT,
            "image_url": "https://example.com/image2.jpg"
        },
        {
            "name": "Medieval Times",
            "description": "Окунись в эпоху рыцарей, замков и великих сражений. Создай свое королевство и стань легендой!",
            "download_url": "https://www.curseforge.com/minecraft/modpacks/medieval-times",
            "build_type": BuildType.SURVIVAL,
            "style": BuildStyle.MEDIEVAL, 
            "difficulty": Difficulty.BEGINNER,
            "image_url": "https://example.com/image3.jpg"
        },
        {
            "name": "Apocalypse Survival",
            "description": "Выживай в постапокалиптическом мире, полном опасностей и тайн. Найди ресурсы, построй укрытие и выживай любой ценой.",
            "download_url": "https://www.curseforge.com/minecraft/modpacks/apocalypse-survival",
            "build_type": BuildType.HARDCORE,
            "style": BuildStyle.POSTAPOCALYPTIC,
            "difficulty": Difficulty.EXPERT,
            "image_url": "https://example.com/image4.jpg"
        },
        {
            "name": "Fairy Tale World",
            "description": "Мир сказок и чудес ждет тебя! Встречай фей, гномов и других волшебных существ в этой красочной сборке.",
            "download_url": "https://www.curseforge.com/minecraft/modpacks/fairy-tale-world", 
            "build_type": BuildType.ADVENTURE,
            "style": BuildStyle.FAIRYTALE,
            "difficulty": Difficulty.BEGINNER,
            "image_url": "https://example.com/image5.jpg"
        }
    ]
    
    for build_data in test_builds:
        await build_crud.create_build(**build_data)
        print(f"✅ Добавлена сборка: {build_data['name']}")
    
    print("🎉 База данных успешно наполнена тестовыми данными!")

if __name__ == "__main__":
    asyncio.run(seed_database())