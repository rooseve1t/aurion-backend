#!/usr/bin/env python3
"""
Запуск сервера Aurion OS
"""
import sys
from pathlib import Path

# Добавляем текущую директорию в Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Запуск FastAPI сервера"""
    try:
        # Запускаем uvicorn
        import uvicorn
        
        print("🚀 Запуск Aurion OS API Server...")
        print("📱 API будет доступен на: http://localhost:8000")
        print("📖 Документация: http://localhost:8000/docs")
        print("🎯 Health check: http://localhost:8000/health")
        print("="*50)
        
        uvicorn.run(
            "app.main_fastapi_fixed:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь что все зависимости установлены:")
        print("   pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
