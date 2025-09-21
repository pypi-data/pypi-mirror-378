#!/usr/bin/env python3
"""
Ультра-простой OpenIDE Client
Импортируй и используй - никаких классов!
"""

# from global_openide import *  # Зависимость добавлена в requirements.txt

# === ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ===

if __name__ == "__main__":
    print("=== УЛЬТРА-ПРОСТЫЕ ПРИМЕРЫ ===")
    
    # Просто импортируй и используй!
    print("=== ПРОСТО ИСПОЛЬЗУЙ ===")
    
    # Python код
    print("Python:", py("print('Привет из ультра-простого OpenIDE!')"))
    print("Math:", py("print(2 + 2 * 3)"))
    
    # Shell команды
    print("Shell:", sh("echo 'Hello World'"))
    print("Pwd:", pwd())
    print("Whoami:", whoami())
    
    # Работа с файлами
    print("\n=== ФАЙЛЫ ===")
    file_create("hello.py", "print('Hello from file!')")
    content = file_read("hello.py")
    print("Файл:", content)
    
    # Выполнение
    result = run_python("hello.py")
    print("Результат:", result)
    
    # Список файлов
    files = ls()
    print("Файлы:", files)
    
    # Виртуальные окружения
    print("\n=== VENV ===")
    venv_create("testenv")
    venv_activate()
    pip_install("requests")
    packages = pip_list()
    print("Пакеты:", packages)
    
    # Система
    print("\n=== СИСТЕМА ===")
    print("Date:", date())
    print("Uptime:", uptime())
    print("Memory:", free())
    print("Disk:", df())
    print("Processes:", ps())
    
    print("\n=== ГОТОВО! ===")
    print("Теперь просто импортируй: from ultra_simple_openide import *")
    print("И используй: py('print(\"hello\")')")
