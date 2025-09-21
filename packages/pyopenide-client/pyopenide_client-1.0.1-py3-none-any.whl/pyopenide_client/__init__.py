#!/usr/bin/env python3
"""
PyOpenIDE Client - Упрощенные клиенты для OpenIDE
Коллекция упрощенных клиентов с разными уровнями простоты синтаксиса
"""

__version__ = "1.0.1"
__author__ = "OpenIDE Team"
__email__ = "openide@example.com"

# Импорты всех упрощенных клиентов
from .simple_client import SimpleOpenIDE
from .magic_client import MagicOpenIDE, ide
from .decorator_client import openide, python, shell, run
from .global_client import *
from .ultra_simple import *

# Добавляем зависимость global_openide
try:
    import global_openide
    GLOBAL_OPENIDE_AVAILABLE = True
except ImportError:
    GLOBAL_OPENIDE_AVAILABLE = False

# Основные классы и функции
__all__ = [
    # Простой клиент
    'SimpleOpenIDE',
    
    # Магический клиент
    'MagicOpenIDE', 'ide',
    
    # Декораторный клиент
    'openide', 'python', 'shell', 'run',
    
    # Глобальные функции (из global_client)
    'py', 'sh', 'cmd', 'file_create', 'file_read', 'file_delete',
    'folder_create', 'folder_list', 'venv_create', 'venv_activate',
    'pip_install', 'pip_list', 'run_python', 'run_shell',
    'ls', 'pwd', 'whoami', 'echo', 'cat', 'mkdir', 'rmdir',
    'touch', 'rm', 'cp', 'mv', 'chmod', 'grep', 'find',
    'ps', 'top', 'df', 'free', 'uptime', 'date', 'uname',
    'env', 'which', 'whereis', 'man', 'help', 'version', 'clear', 'exit',
    
    # Ультра-простые функции (из ultra_simple)
    # Все функции из global_client уже импортированы через *
]

# Информация о пакете
def get_info():
    """Получить информацию о пакете"""
    return {
        "name": "pyopenide-client",
        "version": __version__,
        "description": "Упрощенные клиенты для OpenIDE с разными уровнями простоты синтаксиса",
        "author": __author__,
        "email": __email__,
        "global_openide_available": GLOBAL_OPENIDE_AVAILABLE,
        "clients": [
            "SimpleOpenIDE - Простой клиент с методами",
            "MagicOpenIDE - Магический клиент с атрибутами", 
            "openide decorator - Декораторный клиент",
            "Global functions - Глобальные функции",
            "Ultra-simple - Ультра-простые функции"
        ]
    }

def check_global_openide():
    """Проверить доступность global_openide"""
    return GLOBAL_OPENIDE_AVAILABLE

# Быстрый старт
def quick_start():
    """Быстрый старт с ультра-простым синтаксисом"""
    print("🚀 PyOpenIDE Client - Быстрый старт")
    print("=" * 50)
    print("1. Импортируй все функции:")
    print("   from pyopenide_client import *")
    print()
    print("2. Используй простые функции:")
    print("   print(py('print(\"Hello OpenIDE!\")'))")
    print("   print(sh('echo \"Hello World\"'))")
    print("   print(pwd())")
    print("   print(whoami())")
    print()
    print("3. Работай с файлами:")
    print("   file_create('test.py', 'print(\"Hello!\")')")
    print("   content = file_read('test.py')")
    print("   result = run_python('test.py')")
    print()
    print("4. Создавай виртуальные окружения:")
    print("   venv_create('myenv')")
    print("   venv_activate()")
    print("   pip_install('requests')")
    print()
    print("5. Системные команды:")
    print("   print(date())")
    print("   print(uptime())")
    print("   print(free())")
    print("   print(ps())")
    print()
    print("🎯 Готово! Теперь ты можешь использовать OpenIDE с простым синтаксисом!")
    print("📖 Подробнее: https://pypi.org/project/pyopenide-client/")

if __name__ == "__main__":
    quick_start()
