import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from .quantum_service import QuantumService

logger = logging.getLogger("jarvis-quantum-storage")

class QuantumCloudStorage:
    """Сервис квантового облачного хранилища (Stage 21)"""
    
    def __init__(self, quantum_service: QuantumService, storage_path: str = "vault/quantum_cloud"):
        self.quantum = quantum_service
        self.base_path = Path(storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def store_file(self, filename: str, content: str, node_id: str, token: str) -> Dict[str, Any]:
        """Зашифровать и сохранить файл с использованием квантового ключа"""
        # Zero Trust проверка
        if not self.quantum.quantum_mesh.verify_node(node_id, token):
            return {"success": False, "error": "Zero Trust verification failed"}

        # Получаем квантовый ключ для узла
        node = self.quantum.quantum_mesh.nodes.get(node_id)
        if not node:
            return {"success": False, "error": "Node not found"}
            
        key = node.keys.get("master")
        if not key:
            return {"success": False, "error": "Quantum key not available"}

        # Шифруем данные
        encrypted_data = self.quantum.quantum_mesh.encrypt_data(content, key)
        
        # Сохраняем файл
        file_path = self.base_path / f"{filename}.qenc"
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
            
        logger.info(f"🔒 Vault: File '{filename}' stored with Quantum-AES-256.")
        
        return {
            "success": True,
            "filename": filename,
            "path": str(file_path),
            "node_id": node_id,
            "encryption": "Quantum-AES-256"
        }

    async def retrieve_file(self, filename: str, node_id: str, token: str) -> Optional[str]:
        """Расшифровать и прочитать файл"""
        if not self.quantum.quantum_mesh.verify_node(node_id, token):
            return None

        file_path = self.base_path / f"{filename}.qenc"
        if not file_path.exists():
            return None

        node = self.quantum.quantum_mesh.nodes.get(node_id)
        key = node.keys.get("master")
        
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
            
        return self.quantum.quantum_mesh.decrypt_data(encrypted_data, key)
