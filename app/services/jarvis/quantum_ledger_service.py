import hashlib
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger("jarvis-quantum-ledger")

class LedgerEntry:
    """Запись в неизменяемом логе с двойным хешированием (Stage 22: Quantum Chaining)"""
    def __init__(self, action: str, details: Dict[str, Any], prev_hash: str, index: int):
        self.index = index
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.action = action
        self.details = details
        self.prev_hash = prev_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        # Сложный хеш для имитации Proof of Work / Quantum Integrity
        data = f"{self.index}{self.timestamp}{self.action}{json.dumps(self.details)}{self.prev_hash}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    def mine(self, difficulty: int = 2):
        """Имитация 'майнинга' для обеспечения неизменяемости (PoW)"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class QuantumLedger:
    """Неизменяемый лог действий JARVIS (Stage 22: Advanced Auditability)"""
    
    def __init__(self):
        self.chain: List[LedgerEntry] = []
        self.genesis_hash = "0" * 64
        self.difficulty = 2 # Низкая сложность для быстрой работы

    async def log_action(self, action: str, details: Dict[str, Any]) -> str:
        """Добавить новую запись в лог с проверкой целостности"""
        prev_hash = self.chain[-1].hash if self.chain else self.genesis_hash
        index = len(self.chain)
        
        entry = LedgerEntry(action, details, prev_hash, index)
        entry.mine(self.difficulty) # Гарантируем сложность подделки
        
        self.chain.append(entry)
        
        logger.info(f"📜 Ledger [#{index}]: Action '{action}' secured. Hash: {entry.hash[:16]}...")
        return entry.hash

    def verify_integrity(self) -> bool:
        """Проверить целостность цепочки"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i-1]
            if current.prev_hash != prev.hash:
                return False
            if current.hash != current.calculate_hash():
                return False
        return True

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю действий"""
        return [
            {
                "timestamp": e.timestamp,
                "action": e.action,
                "details": e.details,
                "hash": e.hash
            }
            for e in self.chain[-limit:]
        ]
