"""
Сервис финансового модуля с шифрованием и банковскими API
"""
import asyncio
import json
import hashlib
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet
import aiohttp
from fastapi import Depends

from ..models.finance import BankConnection, BankAccount, Transaction
from ..database import get_db

# Redis для кэширования
redis_client: Optional[redis.Redis] = None

# Шифрование
encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(encryption_key.encode())


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis = redis_client
        
        # API ключи банков
        self.bank_configs = {
            "sber": {
                "client_id": os.getenv("SBER_CLIENT_ID", ""),
                "client_secret": os.getenv("SBER_CLIENT_SECRET", ""),
                "api_url": "https://api.sberbank.ru"
            },
            "tinkoff": {
                "client_id": os.getenv("TINKOFF_CLIENT_ID", ""),
                "client_secret": os.getenv("TINKOFF_CLIENT_SECRET", ""),
                "api_url": "https://openapi.tinkoff.ru"
            },
            "alpha": {
                "client_id": os.getenv("ALPHA_CLIENT_ID", ""),
                "client_secret": os.getenv("ALPHA_CLIENT_SECRET", ""),
                "api_url": "https://api.alfabank.ru"
            }
        }
    
    async def connect_bank(
        self,
        user_id: str,
        bank_code: str,
        redirect_uri: str = None
    ) -> Dict[str, Any]:
        """Подключение банка"""
        
        if bank_code not in self.bank_configs:
            return {
                "status": "error",
                "error": f"Bank {bank_code} not supported"
            }
        
        config = self.bank_configs[bank_code]
        
        # Проверка существующего подключения
        existing = await self._get_bank_connection(user_id, bank_code)
        if existing:
            return {
                "status": "error",
                "error": "Bank already connected"
            }
        
        # Генерация OAuth URL
        auth_url = await self._generate_oauth_url(bank_code, redirect_uri)
        
        # Создание подключения
        connection = BankConnection(
            user_id=user_id,
            bank_code=bank_code,
            bank_name=self._get_bank_name(bank_code),
            client_id=config["client_id"],
            is_connected=False
        )
        
        self.db.add(connection)
        await self.db.commit()
        await self.db.refresh(connection)
        
        return {
            "status": "success",
            "connection_id": str(connection.id),
            "auth_url": auth_url,
            "bank_name": connection.bank_name
        }
    
    async def complete_oauth(
        self,
        connection_id: str,
        code: str
    ) -> Dict[str, Any]:
        """Завершение OAuth процесса"""
        
        connection = await self._get_connection_by_id(connection_id)
        if not connection:
            return {
                "status": "error",
                "error": "Connection not found"
            }
        
        # Обмен кода на токены
        tokens = await self._exchange_code_for_tokens(connection.bank_code, code)
        
        if not tokens:
            return {
                "status": "error",
                "error": "Failed to exchange code for tokens"
            }
        
        # Шифрование и сохранение токенов
        connection.access_token = cipher_suite.encrypt(tokens["access_token"].encode()).decode()
        if "refresh_token" in tokens:
            connection.refresh_token = cipher_suite.encrypt(tokens["refresh_token"].encode()).decode()
        
        connection.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600))
        connection.is_connected = True
        connection.last_sync_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        # Синхронизация аккаунтов
        await self._sync_bank_accounts(connection)
        
        return {
            "status": "success",
            "connected": True
        }
    
    async def get_accounts(self, user_id: str, bank_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получение банковских счетов"""
        
        from sqlalchemy import select
        
        stmt = select(BankAccount).join(BankConnection).where(
            BankConnection.user_id == user_id,
            BankConnection.is_connected == True
        )
        
        if bank_code:
            stmt = stmt.where(BankConnection.bank_code == bank_code)
        
        result = await self.db.execute(stmt)
        accounts = result.scalars().all()
        
        return [
            {
                "id": str(account.id),
                "name": account.account_name,
                "type": account.account_type,
                "currency": account.currency,
                "balance": account.balance,
                "available_balance": account.available_balance,
                "bank_code": account.bank_connection.bank_code,
                "last_sync": account.last_sync_at.isoformat() if account.last_sync_at else None
            }
            for account in accounts
        ]
    
    async def get_transactions(
        self,
        user_id: str,
        account_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение транзакций"""
        
        from sqlalchemy import select, and_, or_
        
        stmt = select(Transaction).join(BankAccount).join(BankConnection).where(
            BankConnection.user_id == user_id
        )
        
        conditions = []
        
        if account_id:
            conditions.append(Transaction.account_id == account_id)
        
        if category:
            conditions.append(or_(
                Transaction.category == category,
                Transaction.ai_category == category
            ))
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(Transaction.transaction_date.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(stmt)
        transactions = result.scalars().all()
        
        # Классификация транзакций
        classified_transactions = []
        for transaction in transactions:
            classified = await self._classify_transaction(transaction)
            classified_transactions.append(classified)
        
        return {
            "transactions": classified_transactions,
            "total": len(classified_transactions),
            "has_more": len(classified_transactions) == limit
        }
    
    async def get_analytics(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Получение финансовой аналитики"""
        
        from sqlalchemy import select, func, and_
        
        since_date = datetime.now(timezone.utc) - timedelta(days=period_days)
        
        # Общие статистики
        stmt = select(
            func.sum(Transaction.amount).label("total_spent"),
            func.count(Transaction.id).label("transaction_count"),
            func.avg(Transaction.amount).label("avg_amount")
        ).join(BankAccount).join(BankConnection).where(
            and_(
                BankConnection.user_id == user_id,
                Transaction.transaction_type == "debit",
                Transaction.transaction_date >= since_date
            )
        )
        
        result = await self.db.execute(stmt)
        stats = result.first()
        
        # По категориям
        category_stmt = select(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        ).join(BankAccount).join(BankConnection).where(
            and_(
                BankConnection.user_id == user_id,
                Transaction.transaction_type == "debit",
                Transaction.transaction_date >= since_date,
                Transaction.category.isnot(None)
            )
        ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc())
        
        category_result = await self.db.execute(category_stmt)
        categories = dict(category_result.fetchall())
        
        # Временной тренд
        trend_stmt = select(
            func.date(Transaction.transaction_date).label("date"),
            func.sum(Transaction.amount).label("daily_spending")
        ).join(BankAccount).join(BankConnection).where(
            and_(
                BankConnection.user_id == user_id,
                Transaction.transaction_type == "debit",
                Transaction.transaction_date >= since_date
            )
        ).group_by(func.date(Transaction.transaction_date)).order_by(func.date(Transaction.transaction_date))
        
        trend_result = await self.db.execute(trend_stmt)
        daily_trend = dict(trend_result.fetchall())
        
        # Генерация советов
        tips = await self._generate_financial_tips(categories, stats.total_spent or 0)
        
        return {
            "period_days": period_days,
            "total_spent": float(stats.total_spent or 0),
            "transaction_count": stats.transaction_count or 0,
            "avg_amount": float(stats.avg_amount or 0),
            "categories": categories,
            "daily_trend": {str(k): float(v) for k, v in daily_trend.items()},
            "tips": tips
        }
    
    async def get_financial_tips(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение финансовых советов"""
        
        analytics = await self.get_analytics(user_id, 30)
        
        return await self._generate_financial_tips(
            analytics["categories"],
            analytics["total_spent"]
        )
    
    async def sync_bank_data(self, user_id: str, bank_code: Optional[str] = None) -> Dict[str, Any]:
        """Синхронизация данных с банками"""
        
        connections = await self._get_user_connections(user_id, bank_code)
        
        results = []
        for connection in connections:
            if connection.is_connected:
                try:
                    # Синхронизация транзакций
                    await self._sync_transactions(connection)
                    results.append({
                        "bank_code": connection.bank_code,
                        "status": "success",
                        "synced_at": datetime.now(timezone.utc).isoformat()
                    })
                except Exception as e:
                    results.append({
                        "bank_code": connection.bank_code,
                        "status": "error",
                        "error": str(e)
                    })
        
        return {
            "status": "completed",
            "results": results
        }
    
    async def _get_bank_connection(self, user_id: str, bank_code: str) -> Optional[BankConnection]:
        """Получение подключения к банку"""
        
        from sqlalchemy import select
        
        stmt = select(BankConnection).where(
            BankConnection.user_id == user_id,
            BankConnection.bank_code == bank_code
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_connection_by_id(self, connection_id: str) -> Optional[BankConnection]:
        """Получение подключения по ID"""
        
        from sqlalchemy import select
        
        stmt = select(BankConnection).where(BankConnection.id == connection_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_user_connections(self, user_id: str, bank_code: Optional[str] = None) -> List[BankConnection]:
        """Получение всех подключений пользователя"""
        
        from sqlalchemy import select
        
        stmt = select(BankConnection).where(BankConnection.user_id == user_id)
        
        if bank_code:
            stmt = stmt.where(BankConnection.bank_code == bank_code)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    def _get_bank_name(self, bank_code: str) -> str:
        """Получение названия банка"""
        
        names = {
            "sber": "Сбербанк",
            "tinkoff": "Тинькофф",
            "alpha": "Альфа-Банк"
        }
        
        return names.get(bank_code, bank_code.upper())
    
    async def _generate_oauth_url(self, bank_code: str, redirect_uri: str) -> str:
        """Генерация OAuth URL"""
        
        config = self.bank_configs[bank_code]
        
        # Заглушка - в реальности здесь специфичная для банка логика
        base_url = config["api_url"]
        client_id = config["client_id"]
        
        return f"{base_url}/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    
    async def _exchange_code_for_tokens(self, bank_code: str, code: str) -> Optional[Dict[str, Any]]:
        """Обмен кода на токены"""
        
        config = self.bank_configs[bank_code]
        
        # Заглушка - в реальности здесь HTTP запрос к банку
        return {
            "access_token": f"mock_token_{bank_code}_{hash(code)}",
            "refresh_token": f"mock_refresh_{bank_code}_{hash(code)}",
            "expires_in": 3600
        }
    
    async def _sync_bank_accounts(self, connection: BankConnection):
        """Синхронизация банковских счетов"""
        
        # Заглушка - в реальности здесь API запрос к банку
        mock_accounts = [
            {
                "external_id": "acc_1",
                "account_number": "****1234",
                "account_name": "Основной счет",
                "account_type": "checking",
                "currency": "RUB",
                "balance": 50000.0,
                "available_balance": 45000.0
            },
            {
                "external_id": "acc_2",
                "account_number": "****5678",
                "account_name": "Накопительный счет",
                "account_type": "savings",
                "currency": "RUB",
                "balance": 150000.0,
                "available_balance": 150000.0
            }
        ]
        
        for account_data in mock_accounts:
            # Проверка существования
            from sqlalchemy import select
            
            stmt = select(BankAccount).where(
                BankAccount.bank_connection_id == connection.id,
                BankAccount.external_id == account_data["external_id"]
            )
            
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Обновление баланса
                existing.balance = account_data["balance"]
                existing.available_balance = account_data["available_balance"]
                existing.last_sync_at = datetime.now(timezone.utc)
            else:
                # Создание нового счета
                account = BankAccount(
                    bank_connection_id=connection.id,
                    user_id=connection.user_id,
                    external_id=account_data["external_id"],
                    account_number=account_data["account_number"],
                    account_name=account_data["account_name"],
                    account_type=account_data["account_type"],
                    currency=account_data["currency"],
                    balance=account_data["balance"],
                    available_balance=account_data["available_balance"],
                    last_sync_at=datetime.now(timezone.utc)
                )
                
                self.db.add(account)
        
        await self.db.commit()
    
    async def _sync_transactions(self, connection: BankConnection):
        """Синхронизация транзакций"""
        
        # Заглушка - генерация тестовых транзакций
        from sqlalchemy import select
        
        stmt = select(BankAccount).where(BankAccount.bank_connection_id == connection.id)
        result = await self.db.execute(stmt)
        accounts = result.scalars().all()
        
        for account in accounts:
            # Генерация тестовых транзакций за последние 30 дней
            for i in range(30):
                date = datetime.now(timezone.utc) - timedelta(days=i)
                
                # Случайная транзакция
                if i % 3 == 0:  # Каждые 3 дня
                    amount = 1000 + (i * 100)  # Разные суммы
                    description = f"Покупка в магазине #{i}"
                    
                    transaction = Transaction(
                        account_id=account.id,
                        user_id=connection.user_id,
                        external_id=f"txn_{account.id}_{i}",
                        description=description,
                        amount=amount,
                        currency="RUB",
                        transaction_type="debit",
                        transaction_date=date,
                        merchant_name="Магазин",
                        mcc_code=5411  # Grocery stores
                    )
                    
                    self.db.add(transaction)
        
        await self.db.commit()
    
    async def _classify_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """Классификация транзакции"""
        
        # Простая эвристическая классификация
        description_lower = transaction.description.lower()
        
        if any(word in description_lower for word in ["продукт", "еда", "супермаркет"]):
            category = "Продукты"
        elif any(word in description_lower for word in ["такси", "uber", "яндекс"]):
            category = "Транспорт"
        elif any(word in description_lower for word in ["кафе", "ресторан", "кофе"]):
            category = "Рестораны"
        elif any(word in description_lower for word in ["аптека", "лекарств"]):
            category = "Здоровье"
        else:
            category = "Прочее"
        
        # Анализ тональности
        if any(word in description_lower for word in ["штраф", "потеря", "кража"]):
            sentiment = "negative"
        elif any(word in description_lower for word in ["подарок", "бонус", "кэшбэк"]):
            sentiment = "positive"
        else:
            sentiment = "neutral"
        
        # Обновление в базе данных
        transaction.category = category
        transaction.ai_category = category
        transaction.sentiment = sentiment
        
        return {
            "id": str(transaction.id),
            "description": transaction.description,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "category": category,
            "ai_category": category,
            "sentiment": sentiment,
            "transaction_date": transaction.transaction_date.isoformat(),
            "merchant_name": transaction.merchant_name
        }
    
    async def _generate_financial_tips(self, categories: Dict[str, float], total_spent: float) -> List[Dict[str, Any]]:
        """Генерация финансовых советов"""
        
        tips = []
        
        # Анализ категорий
        if categories:
            max_category = max(categories.items(), key=lambda x: x[1])
            
            if max_category[1] > total_spent * 0.3:
                tips.append({
                    "type": "warning",
                    "title": f"Высокие траты на {max_category[0]}",
                    "description": f"На категорию '{max_category[0]}' приходится более 30% ваших расходов ({max_category[1]:.0f}₽). Рассмотрите возможность оптимизации.",
                    "priority": "high"
                })
        
        # Общие советы
        if total_spent > 100000:
            tips.append({
                "type": "suggestion",
                "title": "Оптимизация расходов",
                "description": "Ваши месячные расходы превышают 100 000₽. Рекомендуем составить бюджет и отслеживать крупные покупки.",
                "priority": "medium"
            })
        
        if len(categories) < 3:
            tips.append({
                "type": "info",
                "title": "Диверсификация категорий",
                "description": "Рекомендуем детализировать категории расходов для лучшего контроля финансов.",
                "priority": "low"
            })
        
        # Совет по экономии
        tips.append({
            "type": "suggestion",
            "title": "Накопления",
            "description": "Рекомендуем откладывать 10-20% от дохода на накопления и инвестиции.",
            "priority": "medium"
        })
        
        return tips


async def get_finance_service(db: AsyncSession = Depends(get_db)) -> FinanceService:
    """Зависимость для получения финансового сервиса"""
    return FinanceService(db)


async def init_finance_service():
    """Инициализация финансового сервиса"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
    except Exception as e:
        print(f"Redis connection failed for finance service: {e}")
        redis_client = None
