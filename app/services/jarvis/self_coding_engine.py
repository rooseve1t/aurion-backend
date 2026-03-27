import logging
import subprocess
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger("jarvis-self-coding")

class SelfCodingEngine:
    """Движок самокодинга JARVIS (Stage 21)
    Позволяет JARVIS генерировать и внедрять небольшие расширения функционала.
    """
    
    def __init__(self, base_path: str = "app/services/jarvis/extensions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.active_extensions: Dict[str, Any] = {}

    async def generate_extension(self, name: str, purpose: str, code: str) -> Dict[str, Any]:
        """Сгенерировать и сохранить новое расширение"""
        file_path = self.base_path / f"{name}.py"
        
        try:
            # Записываем код расширения
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f'"""\nGenerated Extension: {name}\nPurpose: {purpose}\n"""\n\n')
                f.write(code)
            
            logger.info(f"🛠️ JARVIS: New extension '{name}' generated.")
            
            # Проверка синтаксиса
            if self._verify_syntax(file_path):
                return {"success": True, "path": str(file_path)}
            else:
                file_path.unlink()
                return {"success": False, "error": "Syntax error in generated code"}
                
        except Exception as e:
            logger.error(f"Error generating extension: {e}")
            return {"success": False, "error": str(e)}

    def _verify_syntax(self, file_path: Path) -> bool:
        """Проверить синтаксис сгенерированного файла"""
        try:
            subprocess.run(["python3", "-m", "py_compile", str(file_path)], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    async def run_extension(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Запустить расширение динамически"""
        # В MVP это будет простая загрузка модуля
        # В будущем - полноценная песочница
        import importlib.util
        
        file_path = self.base_path / f"{name}.py"
        if not file_path.exists():
            return None
            
        spec = importlib.util.spec_from_file_location(name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "run"):
                return await module.run(*args, **kwargs)
        
        return None
