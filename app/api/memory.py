"""
API роутер векторной памяти
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel

from ..database_final import AsyncSessionLocal
from ..services.memory_service import MemoryService
from ..api.auth import get_current_user, get_db_session
from ..models.user import User

router = APIRouter(tags=["memory"])


class MemoryCreate(BaseModel):
    content: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    importance: int = 5
    entry_metadata: Optional[Dict[str, Any]] = None


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    importance: Optional[int] = None
    entry_metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    id: str
    content: str
    title: Optional[str]
    tags: List[str]
    categories: List[str]
    importance: int
    similarity: Optional[float]
    final_score: Optional[float]
    created_at: str
    access_count: int


async def get_memory_service(db: AsyncSession = Depends(get_db_session)) -> MemoryService:
    """Зависимость для получения сервиса памяти"""
    return MemoryService(db)


@router.post("/", response_model=Dict[str, Any])
async def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Создание нового воспоминания"""
    
    memory = await memory_service.add_memory(
        user_id=str(current_user.id),
        content=memory_data.content,
        title=memory_data.title,
        tags=memory_data.tags,
        categories=memory_data.categories,
        importance=memory_data.importance,
        entry_metadata=memory_data.entry_metadata
    )
    
    if isinstance(memory, dict):
        memory_id = str(memory.get("id", ""))
        return {
            "id": memory_id,
            "content": memory_data.content,
            "title": memory_data.title,
            "tags": memory_data.tags or [],
            "categories": memory_data.categories or [],
            "importance": memory_data.importance,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "message": "Memory created successfully"
        }

    return {
        "id": str(memory.id),
        "content": memory.content,
        "title": memory.title,
        "tags": memory.tags or [],
        "categories": memory.categories or [],
        "importance": memory.importance,
        "created_at": memory.created_at.isoformat(),
        "message": "Memory created successfully"
    }


@router.get("/search", response_model=List[MemoryResponse])
async def search_memories(
    query: str = Query(default="", min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    importance_threshold: int = Query(default=1, ge=1, le=10),
    tags_filter: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
) -> List[Dict[str, Any]]:
    """Поиск воспоминаний по смыслу"""
    
    tags_list = None
    if tags_filter:
        tags_list = [tag.strip() for tag in tags_filter.split(",")]
    
    memories = await memory_service.search_memories(
        user_id=str(current_user.id),
        query=query,
        limit=limit,
        importance_threshold=importance_threshold,
        tags_filter=tags_list
    )
    
    return memories


@router.get("/{memory_id}", response_model=Dict[str, Any])
async def get_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Получение воспоминания по ID"""
    
    memory = await memory_service.get_memory_by_id(str(current_user.id), memory_id)
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {
        "id": str(memory.id),
        "content": memory.content,
        "title": memory.title,
        "tags": memory.tags or [],
        "categories": memory.categories or [],
        "importance": memory.importance,
        "entry_metadata": memory.entry_metadata or {},
        "created_at": memory.created_at.isoformat(),
        "updated_at": memory.updated_at.isoformat(),
        "access_count": memory.access_count,
        "last_accessed_at": memory.last_accessed_at.isoformat() if memory.last_accessed_at else None
    }


@router.put("/{memory_id}", response_model=Dict[str, Any])
async def update_memory(
    memory_id: str,
    memory_data: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Обновление воспоминания"""
    
    update_data = memory_data.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    memory = await memory_service.update_memory(
        user_id=str(current_user.id),
        memory_id=memory_id,
        **update_data
    )
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {
        "id": str(memory.id),
        "content": memory.content,
        "title": memory.title,
        "tags": memory.tags or [],
        "categories": memory.categories or [],
        "importance": memory.importance,
        "updated_at": memory.updated_at.isoformat(),
        "message": "Memory updated successfully"
    }


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Удаление воспоминания"""
    
    success = await memory_service.delete_memory(str(current_user.id), memory_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {"message": "Memory deleted successfully"}


@router.get("/category/{category}", response_model=List[Dict[str, Any]])
async def get_memories_by_category(
    category: str,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
) -> List[Dict[str, Any]]:
    """Получение воспоминаний по категории"""
    
    memories = await memory_service.get_memories_by_category(
        user_id=str(current_user.id),
        category=category,
        limit=limit
    )
    
    return [
        {
            "id": str(memory.id),
            "content": memory.content,
            "title": memory.title,
            "tags": memory.tags or [],
            "categories": memory.categories or [],
            "importance": memory.importance,
            "created_at": memory.created_at.isoformat(),
            "access_count": memory.access_count
        }
        for memory in memories
    ]


@router.get("/tags/{tags}", response_model=List[Dict[str, Any]])
async def get_memories_by_tags(
    tags: str,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
) -> List[Dict[str, Any]]:
    """Получение воспоминаний по тегам"""
    
    tags_list = [tag.strip() for tag in tags.split(",")]
    
    memories = await memory_service.get_memories_by_tags(
        user_id=str(current_user.id),
        tags=tags_list,
        limit=limit
    )
    
    return [
        {
            "id": str(memory.id),
            "content": memory.content,
            "title": memory.title,
            "tags": memory.tags or [],
            "categories": memory.categories or [],
            "importance": memory.importance,
            "created_at": memory.created_at.isoformat(),
            "access_count": memory.access_count
        }
        for memory in memories
    ]


@router.get("/stats", response_model=Dict[str, Any])
async def get_memory_stats(
    current_user: User = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Получение статистики памяти"""
    
    stats = await memory_service.get_memory_stats(str(current_user.id))
    
    return stats
