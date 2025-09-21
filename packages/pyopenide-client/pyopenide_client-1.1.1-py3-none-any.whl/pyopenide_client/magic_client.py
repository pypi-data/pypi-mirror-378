#!/usr/bin/env python3
"""
Магический OpenIDE Client
Самый простой синтаксис для работы с OpenIDE
"""

import requests
import json
from typing import Dict, List, Optional, Any

class MagicOpenIDE:
    """Магический клиент с упрощенным синтаксисом"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self._container_id = None
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Выполнение HTTP запроса"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    # === МАГИЧЕСКИЕ МЕТОДЫ ===
    
    def __call__(self, command: str) -> str:
        """Выполнить команду: ide('ls -la')"""
        if not self._container_id:
            self._container_id = self._create_container()
        
        result = self._request('POST', f'/api/containers/{self._container_id}/exec', {
            'command': command
        })
        return result.get('output', '')
    
    def __getattr__(self, name: str):
        """Магические атрибуты: ide.python, ide.shell, etc."""
        if name == 'python':
            return lambda code: self(f"python -c \"{code}\"")
        elif name == 'shell':
            return lambda cmd: self(f"bash -c \"{cmd}\"")
        elif name == 'pip':
            return lambda pkg: self(f"localpip install {pkg}")
        elif name == 'venv':
            return lambda name="venv", version="3.12.1": self(f"venv {name}{{{version}}}")
        elif name == 'file':
            return FileManager(self)
        elif name == 'folder':
            return FolderManager(self)
        elif name == 'run':
            return lambda cmd: self(f"run: {cmd}")
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def _create_container(self) -> str:
        """Создать контейнер"""
        result = self._request('POST', '/api/containers', {
            'image': 'python:3.12',
            'command': 'bash'
        })
        return result.get('container_id', '')
    
    def __enter__(self):
        """Контекстный менеджер"""
        self._container_id = self._create_container()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Очистка при выходе"""
        if self._container_id:
            self._request('DELETE', f'/api/containers/{self._container_id}')

class FileManager:
    """Менеджер файлов"""
    
    def __init__(self, ide):
        self.ide = ide
    
    def create(self, filename: str, content: str = "") -> str:
        """Создать файл: ide.file.create('test.py', 'print("hello")')"""
        return self.ide(f"file create filename{{{filename}}}")
    
    def read(self, filename: str) -> str:
        """Прочитать файл: ide.file.read('test.py')"""
        return self.ide(f"file open filename{{{filename}}} as:readonly")
    
    def delete(self, filename: str) -> str:
        """Удалить файл: ide.file.delete('test.py')"""
        return self.ide(f"file delete filename{{{filename}}}")
    
    def list(self) -> str:
        """Список файлов: ide.file.list()"""
        return self.ide("directory cdirectlist")

class FolderManager:
    """Менеджер папок"""
    
    def __init__(self, ide):
        self.ide = ide
    
    def create(self, name: str) -> str:
        """Создать папку: ide.folder.create('mydir')"""
        return self.ide(f"folder create foldername{{{name}}}")
    
    def list(self, name: str = "") -> str:
        """Список файлов: ide.folder.list('mydir')"""
        if name:
            return self.ide(f"folder list folder{{{name}}}")
        else:
            return self.ide("directory cdirectlist")
    
    def delete(self, name: str) -> str:
        """Удалить папку: ide.folder.delete('mydir')"""
        return self.ide(f"folder delete folder{{{name}}}")

# === ГЛОБАЛЬНЫЕ ФУНКЦИИ ===

def ide(base_url: str = "http://127.0.0.1:5000") -> MagicOpenIDE:
    """Создать магический OpenIDE клиент"""
    return MagicOpenIDE(base_url)

# === ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ===

if __name__ == "__main__":
    print("=== МАГИЧЕСКИЕ ПРИМЕРЫ ===")
    
    # Создаем клиент
    o = ide()
    
    # Простые команды
    print("=== ПРОСТЫЕ КОМАНДЫ ===")
    print("ls:", o("ls -la"))
    print("pwd:", o("pwd"))
    
    # Python код
    print("\n=== PYTHON КОД ===")
    print("Python:", o.python("print('Привет из магического OpenIDE!')"))
    print("Math:", o.python("print(2 + 2 * 3)"))
    
    # Shell команды
    print("\n=== SHELL КОМАНДЫ ===")
    print("Echo:", o.shell("echo 'Hello World'"))
    print("Date:", o.shell("date"))
    
    # Работа с файлами
    print("\n=== РАБОТА С ФАЙЛАМИ ===")
    o.file.create("test.py", "print('Hello from file!')")
    print("Создан файл test.py")
    
    result = o.file.read("test.py")
    print("Содержимое файла:", result)
    
    # Выполнение файла
    print("\n=== ВЫПОЛНЕНИЕ ФАЙЛА ===")
    result = o.run("python{test.py}")
    print("Результат выполнения:", result)
    
    # Работа с папками
    print("\n=== РАБОТА С ПАПКАМИ ===")
    o.folder.create("mydir")
    print("Создана папка mydir")
    
    files = o.folder.list()
    print("Список файлов:", files)
    
    # Контекстный менеджер
    print("\n=== КОНТЕКСТНЫЙ МЕНЕДЖЕР ===")
    with ide() as i:
        print("В контексте:", i("whoami"))
        print("Python:", i.python("import sys; print(sys.version)"))
