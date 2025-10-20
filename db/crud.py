from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Build, BuildType, BuildStyle, Difficulty, Vote, UserActivity
from db.session import async_session

from datetime import datetime, date



class BuildCRUD:
    """CRUD операции для работы со сборками"""
    
    @staticmethod
    async def create_build(
        name: str,
        description: str,
        download_url: str,
        build_type: BuildType,
        style: BuildStyle,
        difficulty: Difficulty,
        image_url: str = None,
        added_by: int = None
    ) -> Build:
        """Создать новую сборку"""
        async with async_session() as session:
            build = Build(
                name=name,
                description=description,
                download_url=download_url,
                build_type=build_type,
                style=style,
                difficulty=difficulty,
                image_url=image_url,
                added_by=added_by
            )
            session.add(build)
            await session.commit()
            await session.refresh(build)
            return build
    
    @staticmethod
    async def get_random_build() -> Build:
        """Получить случайную сборку"""
        async with async_session() as session:
            # Используем limit(1) и first() вместо scalar_one_or_none()
            stmt = select(Build).where(Build.is_approved == True).order_by(func.random()).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()  # Теперь это безопасно, т.к. limit(1)
    
    @staticmethod
    async def get_builds_by_filters(
        build_type: BuildType = None,
        style: BuildStyle = None,
        difficulty: Difficulty = None,
        limit: int = 10
    ) -> list[Build]:
        """Получить сборки по фильтрам"""
        async with async_session() as session:
            stmt = select(Build).where(Build.is_approved == True)
            
            if build_type:
                stmt = stmt.where(Build.build_type == build_type)
            if style:
                stmt = stmt.where(Build.style == style)
            if difficulty:
                stmt = stmt.where(Build.difficulty == difficulty)
                
            stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    @staticmethod
    async def get_build_by_id(build_id: int) -> Build:
        """Получить сборку по ID"""
        async with async_session() as session:
            stmt = select(Build).where(Build.id == build_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    @staticmethod
    async def increment_downloads(build_id: int) -> Build:
        """Увеличить счетчик скачиваний и вернуть обновленную сборку"""
        async with async_session() as session:
            # Получаем сборку с блокировкой для обновления
            stmt = select(Build).where(Build.id == build_id)
            result = await session.execute(stmt)
            build = result.scalar_one_or_none()
            
            if build:
                build.downloads_count += 1
                await session.commit()
                await session.refresh(build)  # Обновляем объект
                return build
            return None
    
    @staticmethod
    async def get_top_builds(limit: int = 10) -> list[Build]:
        """Получить топ сборок по скачиваниям"""
        async with async_session() as session:
            stmt = select(Build).where(Build.is_approved == True).order_by(Build.downloads_count.desc()).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    @staticmethod
    async def get_builds_count() -> int:
        """Получить общее количество сборок"""
        async with async_session() as session:
            stmt = select(func.count(Build.id)).where(Build.is_approved == True)
            result = await session.execute(stmt)
            return result.scalar()

    @staticmethod
    async def add_vote(build_id: int, user_id: int, rating: int) -> dict:
        """Добавить оценку сборке"""
        async with async_session() as session:
            # Проверяем, не голосовал ли уже пользователь
            existing_vote = await session.execute(
                select(Vote).where(
                    Vote.build_id == build_id, 
                    Vote.user_id == user_id
                )
            )
            existing_vote = existing_vote.scalar_one_or_none()
            
            if existing_vote:
                return {'success': False, 'error': 'already_voted'}
            
            # Проверяем существование сборки
            build_stmt = select(Build).where(Build.id == build_id)
            build_result = await session.execute(build_stmt)
            build = build_result.scalar_one_or_none()
            
            if not build:
                return {'success': False, 'error': 'build_not_found'}
            
            # Создаем новую оценку
            vote = Vote(
                build_id=build_id,
                user_id=user_id,
                rating=rating
            )
            session.add(vote)
            
            # Пересчитываем средний рейтинг
            all_votes_stmt = select(Vote.rating).where(Vote.build_id == build_id)
            all_votes_result = await session.execute(all_votes_stmt)
            all_ratings = [v[0] for v in all_votes_result.all()]
            
            # Включая новую оценку
            all_ratings.append(rating)
            
            # Правильно рассчитываем средний рейтинг
            average_rating = sum(all_ratings) / len(all_ratings)
            
            # Обновляем статистику сборки
            build.votes_count = len(all_ratings)
            build.rating = round(average_rating)  # Округляем до целого
            
            await session.commit()
            await session.refresh(build)  # Обновляем объект
            
            return {
                'success': True, 
                'new_rating': build.rating, 
                'votes_count': build.votes_count,
                'average_rating': average_rating  # Для отладки
            }
    
    @staticmethod
    async def get_user_vote(build_id: int, user_id: int) -> Vote:
        """Получить оценку пользователя для сборки"""
        async with async_session() as session:
            stmt = select(Vote).where(
                Vote.build_id == build_id,
                Vote.user_id == user_id
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    @staticmethod
    async def recalculate_all_ratings():
        """Пересчитать рейтинги для всех сборок (для исправления данных)"""
        async with async_session() as session:
            # Получаем все сборки
            builds_stmt = select(Build)
            builds_result = await session.execute(builds_stmt)
            builds = builds_result.scalars().all()
            
            updated_count = 0
            for build in builds:
                # Получаем все оценки для сборки
                votes_stmt = select(Vote.rating).where(Vote.build_id == build.id)
                votes_result = await session.execute(votes_stmt)
                ratings = [v[0] for v in votes_result.all()]
                
                if ratings:
                    average_rating = sum(ratings) / len(ratings)
                    build.votes_count = len(ratings)
                    build.rating = round(average_rating)
                    updated_count += 1
                else:
                    build.votes_count = 0
                    build.rating = 0
            
            await session.commit()
            return updated_count
    
    @staticmethod
    async def get_build_rating_stats(build_id: int) -> dict:
        """Получить статистику рейтинга сборки"""
        async with async_session() as session:
            build = await BuildCRUD.get_build_by_id(build_id)
            if not build:
                return None
            
            # Получаем распределение оценок
            stmt = select(Vote.rating, func.count(Vote.id)).where(
                Vote.build_id == build_id
            ).group_by(Vote.rating)
            
            result = await session.execute(stmt)
            rating_distribution = {row[0]: row[1] for row in result.all()}
            
            return {
                'average_rating': build.rating,
                'votes_count': build.votes_count,
                'distribution': rating_distribution
            }
        
    @staticmethod
    async def delete_build(build_id: int) -> bool:
        """Удалить сборку по ID"""
        async with async_session() as session:
            # Находим сборку
            stmt = select(Build).where(Build.id == build_id)
            result = await session.execute(stmt)
            build = result.scalar_one_or_none()
            
            if not build:
                return False
            
            # Удаляем сборку (каскадно удалятся и голоса благодаря relationship)
            await session.delete(build)
            await session.commit()
            return True
    


class AnalyticsCRUD:
    @staticmethod
    async def log_user_activity(
        user_id: int, 
        action: str, 
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        details: str = None
    ):
        """Логирование активности пользователя"""
        async with async_session() as session:
            activity = UserActivity(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                action=action,
                details=details
            )
            session.add(activity)
            await session.commit()
    
    @staticmethod
    async def get_daily_stats(date: date = None) -> dict:
        """Получить статистику за день"""
        if date is None:
            date = datetime.utcnow().date()
            
        async with async_session() as session:
            # Новые пользователи за день
            new_users_stmt = select(func.count(distinct(UserActivity.user_id))).where(
                func.date(UserActivity.timestamp) == date,
                UserActivity.action == 'start'
            )
            new_users = await session.execute(new_users_stmt)
            new_users_count = new_users.scalar() or 0
            
            # Активные пользователи за день
            active_users_stmt = select(func.count(distinct(UserActivity.user_id))).where(
                func.date(UserActivity.timestamp) == date
            )
            active_users = await session.execute(active_users_stmt)
            active_users_count = active_users.scalar() or 0
            
            # Всего действий за день
            total_actions_stmt = select(func.count(UserActivity.id)).where(
                func.date(UserActivity.timestamp) == date
            )
            total_actions = await session.execute(total_actions_stmt)
            total_actions_count = total_actions.scalar() or 0
            
            return {
                'date': date,
                'new_users': new_users_count,
                'active_users': active_users_count,
                'total_actions': total_actions_count
            }
    
    @staticmethod
    async def get_user_stats(user_id: int) -> dict:
        """Получить статистику по конкретному пользователю"""
        async with async_session() as session:
            # Первое и последнее действие
            first_action_stmt = select(UserActivity).where(
                UserActivity.user_id == user_id
            ).order_by(UserActivity.timestamp.asc()).limit(1)
            
            last_action_stmt = select(UserActivity).where(
                UserActivity.user_id == user_id
            ).order_by(UserActivity.timestamp.desc()).limit(1)
            
            first_action = await session.execute(first_action_stmt)
            last_action = await session.execute(last_action_stmt)
            
            # Количество действий
            actions_count_stmt = select(func.count(UserActivity.id)).where(
                UserActivity.user_id == user_id
            )
            actions_count = await session.execute(actions_count_stmt)
            
            return {
                'first_seen': first_action.scalar_one_or_none(),
                'last_seen': last_action.scalar_one_or_none(),
                'total_actions': actions_count.scalar() or 0
            }
    
    @staticmethod
    async def get_top_actions(limit: int = 10) -> list:
        """Самые популярные действия"""
        async with async_session() as session:
            stmt = select(
                UserActivity.action,
                func.count(UserActivity.id).label('count')
            ).group_by(UserActivity.action).order_by(func.count(UserActivity.id).desc()).limit(limit)
            
            result = await session.execute(stmt)
            return result.all()
    
    @staticmethod
    async def get_total_users() -> int:
        """Общее количество уникальных пользователей"""
        async with async_session() as session:
            stmt = select(func.count(distinct(UserActivity.user_id)))
            result = await session.execute(stmt)
            return result.scalar() or 0
    
    @staticmethod
    async def get_unique_users_from_activity() -> list:
        """Получить список уникальных пользователей из таблицы активности"""
        async with async_session() as session:
            stmt = select(
                UserActivity.user_id,
                UserActivity.username,
                UserActivity.first_name,
                UserActivity.last_name
            ).distinct(UserActivity.user_id)
            
            result = await session.execute(stmt)
            return result.all()
    
    @staticmethod
    async def get_unique_users():
        """Получить список уникальных user_id из user_activity"""
        async with async_session() as session:
            # Получаем все уникальные user_id из таблицы активности
            stmt = select(distinct(UserActivity.user_id))
            result = await session.execute(stmt)
            user_ids = [row[0] for row in result.all()]
            return user_ids


build_crud = BuildCRUD()
analytics_crud = AnalyticsCRUD()