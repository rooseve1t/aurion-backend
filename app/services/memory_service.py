"""
Сервис векторной памяти с pgvector
"""
from typing import List, Optional, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi import Depends
import json

from ..models.memory import MemoryEntry
from ..database import get_db
from ..database import Base

# Модель для эмбеддингов
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
redis_client: Optional[redis.Redis] = None


class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = model
        self.redis = redis_client
    
    async def add_memory(
        self,
        user_id: str,
        content: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        importance: int = 5,
        entry_metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryEntry:
        """Добавление воспоминания с вектором"""
        
        # Генерация эмбеддинга
        embedding = self.model.encode(content, convert_to_numpy=True)
        
        memory = MemoryEntry(
            user_id=user_id,
            content=content,
            title=title,
            embedding=embedding.tolist(),
            tags=tags or [],
            categories=categories or [],
            importance=importance,
            entry_metadata=entry_metadata or {}
        )
        
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        
        # Инвалидация кэша
        await self._invalidate_search_cache(user_id)
        
        return memory
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 20,
        importance_threshold: int = 1,
        tags_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Поиск по смыслу с векторным сходством"""
        
        # Проверка кэша
        cache_key = f"memory_search:{user_id}:{hash(query)}:{limit}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Генерация эмбеддинга запроса
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        # Векторный поиск через pgvector
        sql_query = text("""
            SELECT 
                id,
                content,
                title,
                tags,
                categories,
                importance,
                created_at,
                access_count,
                1 - (embedding <=> :query_vector) as similarity
            FROM memory_entries 
            WHERE user_id = :user_id
                AND importance >= :importance_threshold
                AND (:tags_filter IS NULL OR tags && :tags_filter)
            ORDER BY embedding <=> :query_vector
            LIMIT :limit
        """)
        
        result = await self.db.execute(
            sql_query,
            {
                "user_id": user_id,
                "query_vector": query_embedding.tolist(),
                "importance_threshold": importance_threshold,
                "tags_filter": tags_filter,
                "limit": limit
            }
        )
        
        rows = result.fetchall()
        
        # Формирование результатов
        memories = []
        for row in rows:
            # Комбинированный скор: сходство * важность
            final_score = row.similarity * (1.0 / (row.importance + 1))
            
            memories.append({
                "id": str(row.id),
                "content": row.content,
                "title": row.title,
                "tags": row.tags or [],
                "categories": row.categories or [],
                "importance": row.importance,
                "similarity": float(row.similarity),
                "final_score": final_score,
                "created_at": row.created_at.isoformat(),
                "access_count": row.access_count
            })
        
        # Кэширование результата
        if self.redis:
            await self.redis.setex(cache_key, 300, json.dumps(memories))
        
        # Обновление счетчиков доступа
        memory_ids = [row.id for row in rows]
        await self._update_access_counts(memory_ids)
        
        return memories
    
    async def get_memory_by_id(self, user_id: str, memory_id: str) -> Optional[MemoryEntry]:
        """Получение воспоминания по ID"""
        stmt = select(MemoryEntry).where(
            MemoryEntry.id == memory_id,
            MemoryEntry.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_memory(
        self,
        user_id: str,
        memory_id: str,
        **kwargs
    ) -> Optional[MemoryEntry]:
        """Обновление воспоминания"""
        memory = await self.get_memory_by_id(user_id, memory_id)
        if not memory:
            return None
        
        # Если изменился контент - обновляем эмбеддинг
        if "content" in kwargs:
            content = kwargs["content"]
            embedding = self.model.encode(content, convert_to_numpy=True)
            kwargs["embedding"] = embedding.tolist()
        
        for key, value in kwargs.items():
            setattr(memory, key, value)
        
        await self.db.commit()
        await self.db.refresh(memory)
        
        # Инвалидация кэша
        await self._invalidate_search_cache(user_id)
        
        return memory
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Удаление воспоминания"""
        memory = await self.get_memory_by_id(user_id, memory_id)
        if not memory:
            return False
        
        await self.db.delete(memory)
        await self.db.commit()
        
        # Инвалидация кэша
        await self._invalidate_search_cache(user_id)
        
        return True
    
    async def get_memories_by_category(
        self,
        user_id: str,
        category: str,
        limit: int = 50
    ) -> List[MemoryEntry]:
        """Получение воспоминаний по категории"""
        stmt = select(MemoryEntry).where(
            MemoryEntry.user_id == user_id,
            MemoryEntry.categories.contains([category])
        ).order_by(MemoryEntry.importance.desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_memories_by_tags(
        self,
        user_id: str,
        tags: List[str],
        limit: int = 50
    ) -> List[MemoryEntry]:
        """Получение воспоминаний по тегам"""
        stmt = select(MemoryEntry).where(
            MemoryEntry.user_id == user_id,
            MemoryEntry.tags.overlap(tags)
        ).order_by(MemoryEntry.importance.desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Статистика памяти пользователя"""
        
        # Общее количество
        total_count = await self.db.execute(
            select(func.count(MemoryEntry.id)).where(MemoryEntry.user_id == user_id)
        )
        total = total_count.scalar()
        
        # По категориям
        categories_query = text("""
            SELECT unnest(categories) as category, count(*) as count
            FROM memory_entries
            WHERE user_id = :user_id
            GROUP BY category
            ORDER BY count DESC
        """)
        
        categories_result = await self.db.execute(categories_query, {"user_id": user_id})
        categories = dict(categories_result.fetchall())
        
        # По важности
        importance_query = text("""
            SELECT importance, count(*) as count
            FROM memory_entries
            WHERE user_id = :user_id
            GROUP BY importance
            ORDER BY importance
        """)
        
        importance_result = await self.db.execute(importance_query, {"user_id": user_id})
        importance = dict(importance_result.fetchall())
        
        return {
            "total_memories": total,
            "categories": categories,
            "importance_distribution": importance
        }
    
    async def _update_access_counts(self, memory_ids: List[str]):
        """Обновление счетчиков доступа"""
        await self.db.execute(
            text("UPDATE memory_entries SET access_count = access_count + 1, last_accessed_at = NOW() WHERE id = ANY(:ids)"),
            {"ids": memory_ids}
        )
        await self.db.commit()
    
    async def _invalidate_search_cache(self, user_id: str):
        """Инвалидация кэша поиска"""
        if self.redis:
            pattern = f"memory_search:{user_id}:*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)


async def get_memory_service(db: AsyncSession = Depends(get_db)) -> MemoryService:
    """Зависимость для получения сервиса памяти"""
    return MemoryService(db)
