#!/usr/bin/env python3
"""
Декораторный OpenIDE Client
Самый простой синтаксис с декораторами
"""

import requests
import json
from functools import wraps
from typing import Dict, List, Optional, Any, Callable

class DecoratorOpenIDE:
    """OpenIDE клиент с декораторами"""
    
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
    
    def _get_container(self) -> str:
        """Получить или создать контейнер"""
        if not self._container_id:
            result = self._request('POST', '/api/containers', {
                'image': 'python:3.12',
                'command': 'bash'
            })
            self._container_id = result.get('container_id', '')
        return self._container_id
    
    def _execute(self, command: str) -> str:
        """Выполнить команду"""
        container_id = self._get_container()
        result = self._request('POST', f'/api/containers/{container_id}/exec', {
            'command': command
        })
        return result.get('output', '')
    
    def __del__(self):
        """Очистка при удалении"""
        if self._container_id:
            self._request('DELETE', f'/api/containers/{self._container_id}')

# Глобальный экземпляр
_ide = DecoratorOpenIDE()

# === ДЕКОРАТОРЫ ===

def openide(func: Callable) -> Callable:
    """Декоратор для выполнения функции в OpenIDE"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Выполняем функцию и получаем команду
        command = func(*args, **kwargs)
        if isinstance(command, str):
            return _ide._execute(command)
        return command
    return wrapper

def python(code: str) -> str:
    """Выполнить Python код"""
    return _ide._execute(f"python -c \"{code}\"")

def shell(command: str) -> str:
    """Выполнить shell команду"""
    return _ide._execute(f"bash -c \"{command}\"")

def run(command: str) -> str:
    """Выполнить команду"""
    return _ide._execute(command)

# === ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ===

if __name__ == "__main__":
    print("=== ДЕКОРАТОРНЫЕ ПРИМЕРЫ ===")
    
    # Простые функции
    print("=== ПРОСТЫЕ ФУНКЦИИ ===")
    print("Python:", python("print('Привет из декораторного OpenIDE!')"))
    print("Shell:", shell("echo 'Hello World'"))
    print("Run:", run("ls -la"))
    
    # Декораторы
    print("\n=== ДЕКОРАТОРЫ ===")
    
    @openide
    def hello():
        return "echo 'Hello from decorator!'"
    
    @openide
    def math_calc():
        return "python -c \"print(2 + 2 * 3)\""
    
    @openide
    def file_ops():
        return "file create filename{test.txt}"
    
    print("Hello:", hello())
    print("Math:", math_calc())
    print("File:", file_ops())
    
    # Более сложные примеры
    print("\n=== СЛОЖНЫЕ ПРИМЕРЫ ===")
    
    @openide
    def create_python_script():
        return """
        file create filename{hello.py}
        file open filename{hello.py} as:edit
        echo print('Hello from Python script!') > hello.py
        run: python{hello.py}
        """
    
    result = create_python_script()
    print("Script result:", result)
    
    # Работа с виртуальными окружениями
    print("\n=== VIRTUAL ENVIRONMENTS ===")
    
    @openide
    def setup_venv():
        return """
        venv myenv{3.12.1}
        venv activate
        localpip install requests
        python -c "import requests; print('Requests installed!')"
        """
    
    result = setup_venv()
    print("Venv result:", result)
