#!/usr/bin/env python3
"""
Тест импортов для проверки всех исправлений
"""
import sys
import os

# Добавляем путь к app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Тест всех критичных импортов"""
    
    print("🧪 Тестирование импортов...")
    
    tests = []
    
    # Тест 1: Базовые импорты
    try:
        from database import Base, AsyncSessionLocal, get_db
        tests.append(("✅ Database imports", True))
    except Exception as e:
        tests.append(("❌ Database imports", False, str(e)))
    
    # Тест 2: Модели
    try:
        from models.user import User
        from models.memory import MemoryEntry
        tests.append(("✅ Models imports", True))
    except Exception as e:
        tests.append(("❌ Models imports", False, str(e)))
    
    # Тест 3: Auth модуль
    try:
        from auth import authenticate_user, create_user, verify_token
        tests.append(("✅ Auth imports", True))
    except Exception as e:
        tests.append(("❌ Auth imports", False, str(e)))
    
    # Тест 4: Сервисы
    try:
        from services import MemoryService, VoiceService
        tests.append(("✅ Services imports", True))
    except Exception as e:
        tests.append(("❌ Services imports", False, str(e)))
    
    # Тест 5: API роутеры
    try:
        from api.auth import router as auth_router
        from api.memory import router as memory_router
        tests.append(("✅ API imports", True))
    except Exception as e:
        tests.append(("❌ API imports", False, str(e)))
    
    # Результаты
    print("\n📊 Результаты тестов:")
    passed = 0
    failed = 0
    
    for test in tests:
        status = test[0]
        success = test[1]
        
        if success:
            print(f"  {status}")
            passed += 1
        else:
            print(f"  {status}")
            if len(test) > 2:
                print(f"    Ошибка: {test[2]}")
            failed += 1
    
    print(f"\n🎯 Итог: {passed} пройдено, {failed} провалено")
    
    if failed == 0:
        print("🎉 Все импорты работают корректно!")
        return True
    else:
        print("⚠️ Есть проблемы с импортами")
        return False

if __name__ == "__main__":
    test_imports()
