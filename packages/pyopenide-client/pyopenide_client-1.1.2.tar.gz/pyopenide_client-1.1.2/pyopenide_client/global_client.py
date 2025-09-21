#!/usr/bin/env python3
"""
Глобальный OpenIDE Client
Самый простой синтаксис - просто функции
"""

import requests
import json
from typing import Dict, List, Optional, Any

# Глобальные переменные
_BASE_URL = "http://127.0.0.1:5000"
_SESSION = requests.Session()
_SESSION.headers.update({'Content-Type': 'application/json'})
_CONTAINER_ID = None

def _request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Выполнение HTTP запроса"""
    url = f"{_BASE_URL}{endpoint}"
    try:
        if method.upper() == 'GET':
            response = _SESSION.get(url)
        elif method.upper() == 'POST':
            response = _SESSION.post(url, json=data)
        elif method.upper() == 'DELETE':
            response = _SESSION.delete(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "success": False}

def _get_container() -> str:
    """Получить или создать контейнер"""
    global _CONTAINER_ID
    if not _CONTAINER_ID:
        result = _request('POST', '/api/containers', {
            'image': 'python:3.12',
            'command': 'bash'
        })
        _CONTAINER_ID = result.get('container_id', '')
    return _CONTAINER_ID

def _execute(command: str) -> str:
    """Выполнить команду"""
    container_id = _get_container()
    result = _request('POST', f'/api/containers/{container_id}/exec', {
        'command': command
    })
    return result.get('output', '')

# === ГЛОБАЛЬНЫЕ ФУНКЦИИ ===

def py(code: str) -> str:
    """Выполнить Python код: py('print("hello")')"""
    return _execute(f"python -c \"{code}\"")

def sh(command: str) -> str:
    """Выполнить shell команду: sh('ls -la')"""
    return _execute(f"bash -c \"{command}\"")

def cmd(command: str) -> str:
    """Выполнить команду: cmd('pwd')"""
    return _execute(command)

def file_create(filename: str, content: str = "") -> str:
    """Создать файл: file_create('test.py', 'print("hello")')"""
    return _execute(f"file create filename{{{filename}}}")

def file_read(filename: str) -> str:
    """Прочитать файл: file_read('test.py')"""
    return _execute(f"file open filename{{{filename}}} as:readonly")

def file_delete(filename: str) -> str:
    """Удалить файл: file_delete('test.py')"""
    return _execute(f"file delete filename{{{filename}}}")

def folder_create(name: str) -> str:
    """Создать папку: folder_create('mydir')"""
    return _execute(f"folder create foldername{{{name}}}")

def folder_list(name: str = "") -> str:
    """Список файлов: folder_list('mydir')"""
    if name:
        return _execute(f"folder list folder{{{name}}}")
    else:
        return _execute("directory cdirectlist")

def venv_create(name: str = "venv", version: str = "3.12.1") -> str:
    """Создать виртуальное окружение: venv_create('myenv', '3.12.1')"""
    return _execute(f"venv {name}{{{version}}}")

def venv_activate() -> str:
    """Активировать виртуальное окружение: venv_activate()"""
    return _execute("venv activate")

def pip_install(package: str) -> str:
    """Установить пакет: pip_install('requests')"""
    return _execute(f"localpip install {package}")

def pip_list() -> str:
    """Список пакетов: pip_list()"""
    return _execute("localpip list")

def run_python(script: str) -> str:
    """Запустить Python скрипт: run_python('script.py')"""
    return _execute(f"run: python{{{script}}}")

def run_shell(command: str) -> str:
    """Запустить shell команду: run_shell('ls -la')"""
    return _execute(f"run: system{{{command}}}")

def ls(path: str = "") -> str:
    """Список файлов: ls() или ls('mydir')"""
    if path:
        return _execute(f"folder list folder{{{path}}}")
    else:
        return _execute("directory cdirectlist")

def pwd() -> str:
    """Текущая директория: pwd()"""
    return _execute("pwd")

def whoami() -> str:
    """Текущий пользователь: whoami()"""
    return _execute("whoami")

def echo(text: str) -> str:
    """Вывести текст: echo('Hello World')"""
    return _execute(f"echo '{text}'")

def cat(filename: str) -> str:
    """Показать содержимое файла: cat('file.txt')"""
    return _execute(f"cat {filename}")

def mkdir(name: str) -> str:
    """Создать директорию: mkdir('newdir')"""
    return _execute(f"mkdir {name}")

def rmdir(name: str) -> str:
    """Удалить директорию: rmdir('olddir')"""
    return _execute(f"rmdir {name}")

def touch(filename: str) -> str:
    """Создать пустой файл: touch('file.txt')"""
    return _execute(f"touch {filename}")

def rm(filename: str) -> str:
    """Удалить файл: rm('file.txt')"""
    return _execute(f"rm {filename}")

def cp(source: str, target: str) -> str:
    """Копировать файл: cp('source.txt', 'target.txt')"""
    return _execute(f"cp {source} {target}")

def mv(source: str, target: str) -> str:
    """Переместить файл: mv('old.txt', 'new.txt')"""
    return _execute(f"mv {source} {target}")

def chmod(mode: str, filename: str) -> str:
    """Изменить права: chmod('755', 'script.py')"""
    return _execute(f"chmod {mode} {filename}")

def grep(pattern: str, filename: str) -> str:
    """Поиск в файле: grep('hello', 'file.txt')"""
    return _execute(f"grep '{pattern}' {filename}")

def find(name: str) -> str:
    """Поиск файлов: find('*.py')"""
    return _execute(f"find . -name '{name}'")

def ps() -> str:
    """Список процессов: ps()"""
    return _execute("ps aux")

def top() -> str:
    """Топ процессов: top()"""
    return _execute("top")

def df() -> str:
    """Использование диска: df()"""
    return _execute("df -h")

def free() -> str:
    """Использование памяти: free()"""
    return _execute("free -h")

def uptime() -> str:
    """Время работы: uptime()"""
    return _execute("uptime")

def date() -> str:
    """Текущая дата: date()"""
    return _execute("date")

def uname() -> str:
    """Информация о системе: uname()"""
    return _execute("uname -a")

def env() -> str:
    """Переменные окружения: env()"""
    return _execute("env")

def which(command: str) -> str:
    """Путь к команде: which('python')"""
    return _execute(f"which {command}")

def whereis(command: str) -> str:
    """Где находится команда: whereis('python')"""
    return _execute(f"whereis {command}")

def man(command: str) -> str:
    """Справка по команде: man('ls')"""
    return _execute(f"man {command}")

def help() -> str:
    """Справка OpenIDE: help()"""
    return _execute("help")

def version() -> str:
    """Версия OpenIDE: version()"""
    return _execute("version")

def clear() -> str:
    """Очистить экран: clear()"""
    return _execute("clear")

def exit() -> str:
    """Выход: exit()"""
    return _execute("exit")

# === ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ===

if __name__ == "__main__":
    print("=== ГЛОБАЛЬНЫЕ ФУНКЦИИ ===")
    
    # Простые команды
    print("=== ПРОСТЫЕ КОМАНДЫ ===")
    print("pwd:", pwd())
    print("whoami:", whoami())
    print("date:", date())
    print("uname:", uname())
    
    # Python код
    print("\n=== PYTHON КОД ===")
    print("Python:", py("print('Привет из глобального OpenIDE!')"))
    print("Math:", py("print(2 + 2 * 3)"))
    print("Import:", py("import sys; print(sys.version)"))
    
    # Shell команды
    print("\n=== SHELL КОМАНДЫ ===")
    print("Echo:", sh("echo 'Hello World'"))
    print("Ls:", sh("ls -la"))
    print("Ps:", sh("ps aux"))
    
    # Работа с файлами
    print("\n=== РАБОТА С ФАЙЛАМИ ===")
    file_create("test.py", "print('Hello from file!')")
    print("Создан файл test.py")
    
    content = file_read("test.py")
    print("Содержимое файла:", content)
    
    # Выполнение файла
    result = run_python("test.py")
    print("Результат выполнения:", result)
    
    # Список файлов
    files = ls()
    print("Список файлов:", files)
    
    # Работа с папками
    print("\n=== РАБОТА С ПАПКАМИ ===")
    folder_create("mydir")
    print("Создана папка mydir")
    
    files = folder_list("mydir")
    print("Файлы в папке:", files)
    
    # Виртуальные окружения
    print("\n=== VIRTUAL ENVIRONMENTS ===")
    venv_create("myenv", "3.12.1")
    print("Создано виртуальное окружение")
    
    venv_activate()
    print("Активировано виртуальное окружение")
    
    pip_install("requests")
    print("Установлен requests")
    
    packages = pip_list()
    print("Установленные пакеты:", packages)
    
    # Системная информация
    print("\n=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===")
    print("Uptime:", uptime())
    print("Memory:", free())
    print("Disk:", df())
    print("Processes:", ps())
