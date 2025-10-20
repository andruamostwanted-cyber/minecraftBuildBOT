import asyncio
from db.crud import build_crud
from db.session import init_db

async def fix_all_ratings():
    """Исправить все рейтинги в базе данных"""
    await init_db()
    
    updated_count = await build_crud.recalculate_all_ratings()
    print(f"✅ Обновлено рейтингов: {updated_count} сборок")

if __name__ == "__main__":
    asyncio.run(fix_all_ratings())