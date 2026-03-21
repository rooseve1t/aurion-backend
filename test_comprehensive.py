#!/usr/bin/env python3
"""
🔍 КОМПЛЕКСНАЯ ПРОВЕРКА ОШИБОК AURION OS
"""
import sys
import os
import traceback
from typing import Dict, List, Any

# Добавляем путь к app
sys.path.insert(0, os.path.dirname(__file__))

class ErrorChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
    
    def check_import(self, module_name: str, description: str) -> bool:
        """Проверка импорта модуля"""
        try:
            __import__(module_name)
            self.success.append(f"✅ {description}")
            return True
        except ImportError as e:
            self.errors.append(f"❌ {description}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ {description}: {e}")
            return False
    
    def check_function(self, func, description: str) -> bool:
        """Проверка выполнения функции"""
        try:
            result = func()
            if result:
                self.success.append(f"✅ {description}")
                return True
            else:
                self.errors.append(f"❌ {description}: Функция вернула False")
                return False
        except Exception as e:
            self.errors.append(f"❌ {description}: {e}")
            return False
    
    def check_file_exists(self, filepath: str, description: str) -> bool:
        """Проверка существования файла"""
        try:
            if os.path.exists(filepath):
                self.success.append(f"✅ {description}")
                return True
            else:
                self.errors.append(f"❌ {description}: Файл не существует")
                return False
        except Exception as e:
            self.errors.append(f"❌ {description}: {e}")
            return False
    
    def check_syntax(self, filepath: str, description: str) -> bool:
        """Проверка синтаксиса файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем тип файла по расширению
            if filepath.endswith('.html'):
                # HTML файл - проверяем базовую структуру
                if '<!DOCTYPE html>' in content and '<html' in content:
                    self.success.append(f"✅ {description}")
                    return True
                else:
                    self.errors.append(f"❌ {description}: Некорректная HTML структура")
                    return False
            elif filepath.endswith('.js'):
                # JavaScript файл - проверяем базовую структуру
                if 'const' in content or 'var' in content or 'function' in content:
                    self.success.append(f"✅ {description}")
                    return True
                else:
                    self.errors.append(f"❌ {description}: Некорректная JavaScript структура")
                    return False
            elif filepath.endswith('.py'):
                # Python файл - компилируем
                compile(content, filepath, 'exec')
                self.success.append(f"✅ {description}")
                return True
            else:
                # Другие файлы - просто проверяем на чтение
                self.success.append(f"✅ {description}")
                return True
                
        except SyntaxError as e:
            if filepath.endswith('.py'):
                self.errors.append(f"❌ {description}: Синтаксическая ошибка - {e}")
            else:
                self.errors.append(f"❌ {description}: Ошибка в файле - {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ {description}: {e}")
            return False
    
    def print_results(self):
        """Вывод результатов"""
        print("\n" + "="*60)
        print("🔍 РЕЗУЛЬТАТЫ ПРОВЕРКИ ОШИБОК")
        print("="*60)
        
        if self.success:
            print("\n✅ УСПЕШНО:")
            for item in self.success:
                print(f"  {item}")
        
        if self.warnings:
            print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print("\n❌ ОШИБКИ:")
            for item in self.errors:
                print(f"  {item}")
        
        print(f"\n📊 ИТОГО:")
        print(f"  ✅ Успешно: {len(self.success)}")
        print(f"  ⚠️ Предупреждения: {len(self.warnings)}")
        print(f"  ❌ Ошибки: {len(self.errors)}")
        
        if self.errors:
            print(f"\n🚨 СТАТУС: ЕСТЬ КРИТИЧЕСКИЕ ОШИБКИ!")
            return False
        else:
            print(f"\n🎉 СТАТУС: ВСЕ В ПОРЯДКЕ!")
            return True

def check_database():
    """Проверка базы данных"""
    checker = ErrorChecker()
    
    # Проверка импорта базы данных
    checker.check_import("app.database", "Database модуль")
    
    # Проверка Base класса
    try:
        from app.database import Base
        if hasattr(Base, 'registry'):
            checker.success.append("✅ Base класс имеет registry")
        else:
            checker.errors.append("❌ Base класс не имеет registry")
        
        if hasattr(Base, 'metadata'):
            checker.success.append("✅ Base класс имеет metadata")
        else:
            checker.errors.append("❌ Base класс не имеет metadata")
    except Exception as e:
        checker.errors.append(f"❌ Base класс: {e}")
    
    return checker

def check_models():
    """Проверка моделей"""
    checker = ErrorChecker()
    
    # Проверка импорта моделей
    checker.check_import("app.models.memory", "MemoryEntry модель")
    
    # Проверка создания модели
    try:
        from app.models.memory import MemoryEntry
        # Проверяем атрибуты модели
        required_attrs = ['id', 'user_id', 'content', 'content_type', 'embedding', 'tags', 'metadata']
        for attr in required_attrs:
            if hasattr(MemoryEntry, attr):
                checker.success.append(f"✅ MemoryEntry имеет атрибут {attr}")
            else:
                checker.errors.append(f"❌ MemoryEntry не имеет атрибута {attr}")
    except Exception as e:
        checker.errors.append(f"❌ MemoryEntry: {e}")
    
    return checker

def check_services():
    """Проверка сервисов"""
    checker = ErrorChecker()
    
    # Проверка импорта сервисов
    checker.check_import("app.services.memory_service", "MemoryService")
    checker.check_import("app.services.voice_jarvis_standalone", "VoiceJarvisStandalone")
    
    # Проверка создания экземпляров
    try:
        from app.services.voice_jarvis_standalone import VoiceJarvisStandalone
        jarvis = VoiceJarvisStandalone()
        if hasattr(jarvis, 'jarvis_personality'):
            checker.success.append("✅ VoiceJarvisStandalone создан успешно")
        else:
            checker.errors.append("❌ VoiceJarvisStandalone не имеет personality")
    except Exception as e:
        checker.errors.append(f"❌ VoiceJarvisStandalone: {e}")
    
    return checker

def check_api():
    """Проверка API"""
    checker = ErrorChecker()
    
    # Проверка импорта API
    checker.check_import("app.api.auth", "Auth API")
    checker.check_import("app.api.memory", "Memory API")
    
    # Проверка создания роутеров
    try:
        from app.api.auth import router as auth_router
        if hasattr(auth_router, 'routes'):
            checker.success.append("✅ Auth API роутер создан")
        else:
            checker.errors.append("❌ Auth API роутер не имеет routes")
    except Exception as e:
        checker.errors.append(f"❌ Auth API роутер: {e}")
    
    return checker

def check_main_apps():
    """Проверка основных приложений"""
    checker = ErrorChecker()
    
    # Проверка импорта основных приложений
    checker.check_import("app.main_simple", "Main Simple App")
    checker.check_import("app.main_final", "Main Final App")
    
    # Проверка создания FastAPI приложений
    try:
        from app.main_simple import app as simple_app
        checker.success.append("✅ Main Simple App создан")
    except Exception as e:
        checker.errors.append(f"❌ Main Simple App: {e}")
    
    try:
        from app.main_final import app as final_app
        checker.success.append("✅ Main Final App создан")
    except Exception as e:
        checker.errors.append(f"❌ Main Final App: {e}")
    
    return checker

def check_files():
    """Проверка файлов"""
    checker = ErrorChecker()
    
    # Проверка существования ключевых файлов
    files_to_check = [
        ("app/database.py", "Database файл"),
        ("app/models/memory.py", "Memory модель"),
        ("app/services/memory_service.py", "Memory сервис"),
        ("app/services/voice_jarvis_standalone.py", "JARVIS сервис"),
        ("app/api/auth.py", "Auth API"),
        ("app/main_simple.py", "Main Simple"),
        ("app/main_final.py", "Main Final"),
        ("preview_enhanced.html", "Enhanced Preview"),
        ("manifest.json", "PWA Manifest"),
        ("sw.js", "Service Worker")
    ]
    
    for filepath, description in files_to_check:
        checker.check_file_exists(filepath, description)
        if os.path.exists(filepath):
            checker.check_syntax(filepath, f"Синтаксис {description}")
    
    return checker

def check_dependencies():
    """Проверка зависимостей"""
    checker = ErrorChecker()
    
    # Проверка ключевых зависимостей
    dependencies = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("uvicorn", "Uvicorn"),
        ("redis", "Redis"),
        ("numpy", "NumPy"),
        ("sentence_transformers", "Sentence Transformers"),
        ("openai", "OpenAI"),
        ("aiohttp", "AioHTTP")
    ]
    
    for dep, name in dependencies:
        checker.check_import(dep, name)
    
    return checker

def main():
    """Основная функция"""
    print("🔍 КОМПЛЕКСНАЯ ПРОВЕРКА AURION OS")
    print("="*60)
    
    all_checkers = []
    
    # Проверка всех компонентов
    all_checkers.append(check_database())
    all_checkers.append(check_models())
    all_checkers.append(check_services())
    all_checkers.append(check_api())
    all_checkers.append(check_main_apps())
    all_checkers.append(check_files())
    all_checkers.append(check_dependencies())
    
    # Сбор всех результатов
    total_errors = []
    total_success = []
    total_warnings = []
    
    for checker in all_checkers:
        total_errors.extend(checker.errors)
        total_success.extend(checker.success)
        total_warnings.extend(checker.warnings)
    
    # Вывод результатов
    print("\n" + "="*60)
    print("🔍 ОБЩИЙ ОТЧЕТ ПРОВЕРКИ")
    print("="*60)
    
    if total_success:
        print("\n✅ УСПЕШНО ПРОВЕРЕНО:")
        for item in total_success:
            print(f"  {item}")
    
    if total_warnings:
        print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
        for item in total_warnings:
            print(f"  {item}")
    
    if total_errors:
        print("\n❌ НАЙДЕННЫЕ ОШИБКИ:")
        for item in total_errors:
            print(f"  {item}")
    
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"  ✅ Успешно: {len(total_success)}")
    print(f"  ⚠️ Предупреждения: {len(total_warnings)}")
    print(f"  ❌ Ошибки: {len(total_errors)}")
    
    if total_errors:
        print(f"\n🚨 СТАТУС: НАЙДЕНЫ ОШИБКИ - ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ!")
        print("\n📋 РЕКОМЕНДАЦИИ:")
        print("1. Исправьте критические ошибки в базе данных")
        print("2. Проверьте импорты и зависимости")
        print("3. Убедитесь что все файлы существуют")
        print("4. Запустите проверку снова")
        return False
    else:
        print(f"\n🎉 СТАТУС: ВСЕ КОМПОНЕНТЫ РАБОТАЮТ КОРРЕКТНО!")
        print("\n🚀 Aurion OS готов к запуску!")
        return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print(f"\n🔧 Для исправления ошибок выполните:")
        print(f"python3 {__file__}")
        sys.exit(1)
    else:
        print(f"\n✅ Проверка завершена успешно!")
        sys.exit(0)
