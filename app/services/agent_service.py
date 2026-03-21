"""
Сервис агентов и роевого интеллекта
"""
import asyncio
import json
import uuid
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone, timedelta
from abc import ABC, abstractmethod
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..models.agent import Agent, AgentTask, AgentLog
from ..database import get_db

# Redis для очередей
redis_client: Optional[redis.Redis] = None


class BaseAgent(ABC):
    """Базовый класс для всех агентов"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.is_running = False
    
    @abstractmethod
    async def can_handle(self, task_type: str, input_data: Dict[str, Any]) -> bool:
        """Проверка может ли агент обработать задачу"""
        pass
    
    @abstractmethod
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """Обработка задачи"""
        pass
    
    async def execute_with_retry(self, task: AgentTask, max_retries: int = 3) -> Dict[str, Any]:
        """Выполнение с повторными попытками"""
        
        for attempt in range(max_retries + 1):
            try:
                result = await self.process(task)
                
                # Логирование успеха
                await self._log("info", f"Task completed successfully", {
                    "task_id": str(task.id),
                    "attempt": attempt + 1
                })
                
                return result
                
            except Exception as e:
                if attempt == max_retries:
                    # Последняя попытка неудачна
                    await self._log("error", f"Task failed after {max_retries + 1} attempts", {
                        "task_id": str(task.id),
                        "error": str(e)
                    })
                    
                    return {
                        "status": "failed",
                        "error": str(e)
                    }
                
                # Логирование попытки
                await self._log("warning", f"Task attempt {attempt + 1} failed", {
                    "task_id": str(task.id),
                    "error": str(e)
                })
                
                # Задержка перед повторной попыткой
                await asyncio.sleep(2 ** attempt)
    
    async def _log(self, level: str, message: str, details: Dict[str, Any] = None):
        """Логирование действий агента"""
        
        # В реальности здесь сохранение в AgentLog
        print(f"[{self.agent_id}] {level}: {message}")


class FinancialAgent(BaseAgent):
    """Финансовый агент"""
    
    async def can_handle(self, task_type: str, input_data: Dict[str, Any]) -> bool:
        return task_type in ["analyze_spending", "budget_optimization", "investment_advice"]
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """Обработка финансовых задач"""
        
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "analyze_spending":
            return await self._analyze_spending(input_data)
        elif task_type == "budget_optimization":
            return await self._optimize_budget(input_data)
        elif task_type == "investment_advice":
            return await self._provide_investment_advice(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _analyze_spending(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ расходов"""
        
        # Заглушка - в реальности интеграция с finance_service
        transactions = input_data.get("transactions", [])
        period_days = input_data.get("period_days", 30)
        
        # Простая аналитика
        total_spent = sum(t.get("amount", 0) for t in transactions)
        categories = {}
        
        for transaction in transactions:
            category = transaction.get("category", "Прочее")
            categories[category] = categories.get(category, 0) + transaction.get("amount", 0)
        
        return {
            "status": "completed",
            "analysis": {
                "total_spent": total_spent,
                "period_days": period_days,
                "categories": categories,
                "avg_daily": total_spent / period_days,
                "top_category": max(categories.items(), key=lambda x: x[1]) if categories else None
            },
            "recommendations": [
                "Рассмотрите возможность сокращения расходов на самую крупную категорию",
                "Создайте бюджет для лучшего контроля финансов"
            ]
        }
    
    async def _optimize_budget(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Оптимизация бюджета"""
        
        current_spending = input_data.get("current_spending", {})
        target_budget = input_data.get("target_budget", {})
        
        optimization = {}
        
        for category, current in current_spending.items():
            target = target_budget.get(category, current)
            
            if current > target:
                reduction_needed = current - target
                optimization[category] = {
                    "current": current,
                    "target": target,
                    "reduction_needed": reduction_needed,
                    "suggestions": [
                        f"Сократите расходы на {reduction_needed:.0f}₽",
                        "Найдите альтернативные поставщики услуг",
                        "Отложите ненужные покупки"
                    ]
                }
        
        return {
            "status": "completed",
            "optimization": optimization,
            "total_savings": sum(opt["reduction_needed"] for opt in optimization.values())
        }
    
    async def _provide_investment_advice(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Инвестиционные советы"""
        
        risk_tolerance = input_data.get("risk_tolerance", "medium")
        investment_amount = input_data.get("amount", 10000)
        time_horizon = input_data.get("time_horizon", 12)  # месяцы
        
        advice = []
        
        if risk_tolerance == "low":
            advice.extend([
                "Рассмотрите вклады в надежных банках",
                "Облигации федерального займа",
                "Золотые сертификаты"
            ])
        elif risk_tolerance == "medium":
            advice.extend([
                "Сбалансированный портфель акций и облигаций",
                "ETF на индекс МосБиржи",
                "Корпоративные облигации"
            ])
        else:
            advice.extend([
                "Акции роста технологических компаний",
                "Криптовалюты с высокой капитализацией",
                "Стартап инвестиции"
            ])
        
        return {
            "status": "completed",
            "advice": advice,
            "risk_level": risk_tolerance,
            "recommended_allocation": self._get_allocation_by_risk(risk_tolerance)
        }
    
    def _get_allocation_by_risk(self, risk_tolerance: str) -> Dict[str, float]:
        """Получение рекомендуемой аллокации"""
        
        allocations = {
            "low": {"stocks": 20, "bonds": 70, "cash": 10},
            "medium": {"stocks": 60, "bonds": 30, "cash": 10},
            "high": {"stocks": 80, "bonds": 15, "cash": 5}
        }
        
        return allocations.get(risk_tolerance, allocations["medium"])


class SmartHomeAgent(BaseAgent):
    """Агент умного дома"""
    
    async def can_handle(self, task_type: str, input_data: Dict[str, Any]) -> bool:
        return task_type in ["optimize_energy", "automate_routines", "security_analysis"]
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """Обработка задач умного дома"""
        
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "optimize_energy":
            return await self._optimize_energy(input_data)
        elif task_type == "automate_routines":
            return await self._create_automations(input_data)
        elif task_type == "security_analysis":
            return await self._analyze_security(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _optimize_energy(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Оптимизация энергопотребления"""
        
        devices = input_data.get("devices", [])
        current_consumption = sum(d.get("power_consumption", 0) for d in devices)
        
        # Простая оптимизация
        recommendations = [
            "Выключайте свет в неиспользуемых помещениях",
            "Используйте таймеры для обогревателей",
            "Оптимизируйте работу кондиционера"
        ]
        
        potential_savings = current_consumption * 0.2  # 20% экономия
        
        return {
            "status": "completed",
            "current_consumption": current_consumption,
            "potential_savings": potential_savings,
            "recommendations": recommendations,
            "automation_rules": [
                {
                    "name": "Ночной режим",
                    "condition": "time >= 23:00",
                    "action": "dim_lights_to_30%"
                },
                {
                    "name": "Отсутствие дома",
                    "condition": "no_motion_for_2h",
                    "action": "turn_off_all_lights"
                }
            ]
        }
    
    async def _create_automations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание автоматизаций"""
        
        routines = input_data.get("routines", [])
        
        automations = []
        
        for routine in routines:
            automation = {
                "id": str(uuid.uuid4()),
                "name": routine["name"],
                "triggers": routine["triggers"],
                "conditions": routine.get("conditions", []),
                "actions": routine["actions"],
                "enabled": True
            }
            automations.append(automation)
        
        return {
            "status": "completed",
            "automations": automations,
            "total_created": len(automations)
        }
    
    async def _analyze_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ безопасности"""
        
        devices = input_data.get("devices", [])
        security_score = 100
        
        issues = []
        
        # Проверка замков
        locks = [d for d in devices if d.get("device_type") == "lock"]
        if not locks:
            security_score -= 30
            issues.append("Отсутствуют умные замки")
        
        # Проверка камер
        cameras = [d for d in devices if d.get("device_type") == "camera"]
        if not cameras:
            security_score -= 20
            issues.append("Отсутствуют камеры наблюдения")
        
        # Проверка датчиков движения
        motion_sensors = [d for d in devices if d.get("device_type") == "sensor"]
        if len(motion_sensors) < 2:
            security_score -= 15
            issues.append("Недостаточно датчиков движения")
        
        return {
            "status": "completed",
            "security_score": max(0, security_score),
            "issues": issues,
            "recommendations": [
                "Установите умные замки на все входы",
                "Разместите камеры на ключевых точках",
                "Добавьте датчики движения в коридорах"
            ]
        }


class OSINTAgent(BaseAgent):
    """OSINT агент"""
    
    async def can_handle(self, task_type: str, input_data: Dict[str, Any]) -> bool:
        return task_type in ["threat_analysis", "reputation_check", "asset_discovery"]
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """Обработка OSINT задач"""
        
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "threat_analysis":
            return await self._analyze_threats(input_data)
        elif task_type == "reputation_check":
            return await self._check_reputation(input_data)
        elif task_type == "asset_discovery":
            return await self._discover_assets(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _analyze_threats(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ угроз"""
        
        target = input_data.get("target", "")
        threat_level = "low"
        
        # Заглушка анализа
        if "suspicious" in target.lower():
            threat_level = "high"
        elif "unknown" in target.lower():
            threat_level = "medium"
        
        return {
            "status": "completed",
            "threat_level": threat_level,
            "indicators": [
                "Необычная сетевая активность",
                "Подозрительные домены"
            ],
            "recommendations": [
                "Усиление мониторинга",
                "Проверка репутации"
            ]
        }
    
    async def _check_reputation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка репутации"""
        
        entity = input_data.get("entity", "")
        
        # Заглушка проверки репутации
        reputation_score = 75  # Средняя репутация
        
        return {
            "status": "completed",
            "reputation_score": reputation_score,
            "sources": ["social_media", "news", "forums"],
            "sentiment": "neutral",
            "recommendations": [
                "Мониторить упоминания",
                "Активно управлять репутацией"
            ]
        }
    
    async def _discover_assets(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        "Поиск активов"""
        
        domain = input_data.get("domain", "")
        
        # Заглушка поиска активов
        discovered_assets = [
            {"type": "subdomain", "value": f"api.{domain}"},
            {"type": "subdomain", "value": f"admin.{domain}"},
            {"type": "ip_address", "value": "192.168.1.1"},
            {"type": "technology", "value": "nginx"}
        ]
        
        return {
            "status": "completed",
            "discovered_assets": discovered_assets,
            "total_count": len(discovered_assets),
            "risk_assessment": "medium"
        }


class MemoryAgent(BaseAgent):
    """Агент памяти"""
    
    async def can_handle(self, task_type: str, input_data: Dict[str, Any]) -> bool:
        return task_type in ["memory_analysis", "pattern_detection", "knowledge_extraction"]
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """Обработка задач памяти"""
        
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "memory_analysis":
            return await self._analyze_memories(input_data)
        elif task_type == "pattern_detection":
            return await self._detect_patterns(input_data)
        elif task_type == "knowledge_extraction":
            return await self._extract_knowledge(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _analyze_memories(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ воспоминаний"""
        
        memories = input_data.get("memories", [])
        
        # Простая аналитика
        categories = {}
        emotions = {}
        
        for memory in memories:
            category = memory.get("category", "general")
            emotion = memory.get("emotion", "neutral")
            
            categories[category] = categories.get(category, 0) + 1
            emotions[emotion] = emotions.get(emotion, 0) + 1
        
        return {
            "status": "completed",
            "total_memories": len(memories),
            "categories": categories,
            "emotions": emotions,
            "insights": [
                f"Наиболее частая категория: {max(categories.items(), key=lambda x: x[1])[0]}",
                f"Преобладающая эмоция: {max(emotions.items(), key=lambda x: x[1])[0]}"
            ]
        }
    
    async def _detect_patterns(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обнаружение паттернов"""
        
        memories = input_data.get("memories", [])
        
        # Заглушка обнаружения паттернов
        patterns = [
            {
                "type": "temporal",
                "description": "Активность повышается по вечерам",
                "confidence": 0.8
            },
            {
                "type": "emotional",
                "description": "Позитивные эмоции связаны с работой",
                "confidence": 0.7
            }
        ]
        
        return {
            "status": "completed",
            "patterns": patterns,
            "total_patterns": len(patterns)
        }
    
    async def _extract_knowledge(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение знаний"""
        
        memories = input_data.get("memories", [])
        
        # Заглушка извлечения знаний
        knowledge = [
            {
                "fact": "Предпочитаете работать в спокойной обстановке",
                "confidence": 0.9,
                "source_memories": 3
            },
            {
                "fact": "Цените punctuality",
                "confidence": 0.8,
                "source_memories": 2
            }
        ]
        
        return {
            "status": "completed",
            "knowledge": knowledge,
            "total_facts": len(knowledge)
        }


class AgentOrchestrator:
    """Оркестратор агентов"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.agents = {}
        self.redis = redis_client
        
        # Инициализация агентов
        self._init_agents()
    
    def _init_agents(self):
        """Инициализация всех агентов"""
        
        self.agent_classes = {
            "financial": FinancialAgent,
            "smarthome": SmartHomeAgent,
            "osint": OSINTAgent,
            "memory": MemoryAgent
        }
    
    async def create_agent(
        self,
        user_id: str,
        name: str,
        agent_type: str,
        config: Dict[str, Any]
    ) -> Agent:
        """Создание нового агента"""
        
        if agent_type not in self.agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent = Agent(
            user_id=user_id,
            name=name,
            agent_type=agent_type,
            config=config,
            is_active=True,
            status="idle"
        )
        
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        
        # Создание экземпляра агента
        agent_instance = self.agent_classes[agent_type](str(agent.id), config)
        self.agents[str(agent.id)] = agent_instance
        
        return agent
    
    async def submit_task(
        self,
        user_id: str,
        task_type: str,
        input_data: Dict[str, Any],
        preferred_agent_id: Optional[str] = None
    ) -> AgentTask:
        """Отправка задачи на выполнение"""
        
        # Выбор агента
        agent = await self._select_agent(user_id, task_type, preferred_agent_id)
        
        if not agent:
            raise ValueError("No suitable agent found")
        
        # Создание задачи
        task = AgentTask(
            agent_id=agent.id,
            user_id=user_id,
            task_type=task_type,
            input_data=input_data,
            status="pending",
            priority=5
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        # Отправка в очередь
        await self._enqueue_task(task)
        
        return task
    
    async def execute_swarm_task(
        self,
        user_id: str,
        task_type: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнение роевой задачи"""
        
        # Декомпозиция задачи
        subtasks = await self._decompose_task(task_type, input_data)
        
        # Параллельное выполнение
        tasks = []
        for subtask in subtasks:
            task = await self.submit_task(
                user_id,
                subtask["task_type"],
                subtask["input_data"]
            )
            tasks.append(task)
        
        # Ожидание завершения
        results = []
        for task in tasks:
            result = await self._wait_for_task_completion(task.id, timeout=300)
            results.append(result)
        
        # Агрегация результатов
        aggregated = await self._aggregate_swarm_results(results)
        
        return {
            "swarm_task_id": str(uuid.uuid4()),
            "status": "completed",
            "subtasks": len(subtasks),
            "results": results,
            "aggregated_result": aggregated
        }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса задачи"""
        
        from sqlalchemy import select
        
        stmt = select(AgentTask).where(AgentTask.id == task_id)
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return None
        
        return {
            "id": str(task.id),
            "status": task.status,
            "progress": task.progress,
            "result": task.result,
            "error_message": task.error_message,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }
    
    async def _select_agent(
        self,
        user_id: str,
        task_type: str,
        preferred_agent_id: Optional[str]
    ) -> Optional[Agent]:
        """Выбор подходящего агента"""
        
        from sqlalchemy import select
        
        if preferred_agent_id:
            stmt = select(Agent).where(
                Agent.id == preferred_agent_id,
                Agent.user_id == user_id,
                Agent.is_active == True
            )
        else:
            stmt = select(Agent).where(
                Agent.user_id == user_id,
                Agent.is_active == True,
                Agent.agent_type.in_(list(self.agent_classes.keys()))
            )
        
        result = await self.db.execute(stmt)
        agents = result.scalars().all()
        
        # Проверка может ли агент обработать задачу
        for agent in agents:
            agent_instance = self.agents.get(str(agent.id))
            if agent_instance and await agent_instance.can_handle(task_type, {}):
                return agent
        
        return None
    
    async def _enqueue_task(self, task: AgentTask):
        """Отправка задачи в очередь"""
        
        if self.redis:
            queue_key = f"agent_queue:{task.agent_id}"
            await self.redis.lpush(queue_key, json.dumps({
                "task_id": str(task.id),
                "task_type": task.task_type,
                "priority": task.priority
            }))
    
    async def _decompose_task(self, task_type: str, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Декомпозиция сложной задачи"""
        
        # Простая декомпозиция по ключевым словам
        subtasks = []
        
        if "анализ" in task_type.lower() or "analysis" in task_type.lower():
            subtasks.extend([
                {"task_type": "data_collection", "input_data": input_data},
                {"task_type": "pattern_detection", "input_data": input_data},
                {"task_type": "insight_generation", "input_data": input_data}
            ])
        
        elif "оптимизация" in task_type.lower() or "optimization" in task_type.lower():
            subtasks.extend([
                {"task_type": "current_state_analysis", "input_data": input_data},
                {"task_type": "optimization_calculation", "input_data": input_data},
                {"task_type": "recommendation_generation", "input_data": input_data}
            ])
        
        else:
            subtasks.append({"task_type": task_type, "input_data": input_data})
        
        return subtasks
    
    async def _wait_for_task_completion(self, task_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Ожидание завершения задачи"""
        
        start_time = datetime.now(timezone.utc)
        
        while (datetime.now(timezone.utc) - start_time).seconds < timeout:
            status = await self.get_task_status(task_id)
            
            if status and status["status"] in ["completed", "failed"]:
                return status
            
            await asyncio.sleep(1)
        
        return {"status": "timeout"}
    
    async def _aggregate_swarm_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Агрегация результатов роевых задач"""
        
        successful_results = [r for r in results if r.get("status") == "completed"]
        
        return {
            "total_tasks": len(results),
            "successful_tasks": len(successful_results),
            "success_rate": len(successful_results) / len(results) if results else 0,
            "combined_insights": [r.get("result", {}) for r in successful_results]
        }


async def get_agent_service(db: AsyncSession = Depends(get_db)) -> AgentOrchestrator:
    """Зависимость для получения сервиса агентов"""
    return AgentOrchestrator(db)


async def init_agent_service():
    """Инициализация сервиса агентов"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
    except Exception as e:
        print(f"Redis connection failed for agent service: {e}")
        redis_client = None
