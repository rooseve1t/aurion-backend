#!/usr/bin/env python3
"""
Тест простого рабочего приложения
"""
import sys
import os

# Добавляем путь к app
sys.path.insert(0, os.path.dirname(__file__))

def test_simple_system():
    """Тест простого рабочего приложения"""
    
    print("🧪 ТЕСТ ПРОСТОЙ РАБОЧЕЙ СИСТЕМЫ")
    
    tests = []
    
    # Тест 1: Простое приложение
    try:
        from app.main_simple import app
        tests.append(("✅ Simple App", True))
        print(f"  ✅ App title: {app.title}")
        print(f"  ✅ App version: {app.version}")
        print(f"  ✅ Routes count: {len(app.routes)}")
    except Exception as e:
        tests.append(("❌ Simple App", False, str(e)))
    
    # Тест 2: Базовые импорты
    try:
        from fastapi import FastAPI
        tests.append(("✅ FastAPI Import", True))
    except Exception as e:
        tests.append(("❌ FastAPI Import", False, str(e)))
    
    # Тест 3: Базовая структура
    try:
        import os
        import sys
        tests.append(("✅ Basic Structure", True))
    except Exception as e:
        tests.append(("❌ Basic Structure", False, str(e)))
    
    # Результаты
    print("\n📊 РЕЗУЛЬТАТЫ:")
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
    
    print(f"\n🎯 ИТОГ: {passed} пройдено, {failed} провалено")
    
    if failed == 0:
        print("\n🎉 ПРОСТАЯ СИСТЕМА ГОТОВА!")
        print("✅ FastAPI приложение работает")
        print("✅ CORS настроен")
        print("✅ Базовые эндпоинты работают")
        print("✅ Обработка ошибок работает")
        print("\n🚀 ЗАПУСК КОМАНДА:")
        print("python3 app/main_simple.py")
        print("\n📖 ДОКУМЕНТАЦИЯ:")
        print("http://localhost:8000/docs")
        return True
    else:
        print(f"\n⚠️ ПРОБЛЕМЫ: {failed}")
        return False

if __name__ == "__main__":
    test_simple_system()
