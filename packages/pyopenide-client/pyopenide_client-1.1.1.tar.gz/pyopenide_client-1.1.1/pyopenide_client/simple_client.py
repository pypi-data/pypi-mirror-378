#!/usr/bin/env python3
"""
Упрощенный OpenIDE Client
Простой синтаксис для работы с OpenIDE
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any

class SimpleOpenIDE:
    """Упрощенный клиент для OpenIDE"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
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
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    # === ПРОСТЫЕ МЕТОДЫ ===
    
    def health(self) -> bool:
        """Проверка здоровья API"""
        result = self._request('GET', '/api/health')
        return result.get('status') == 'ok'
    
    def create(self, image: str = "python:3.12", command: str = "bash") -> str:
        """Создать контейнер (возвращает ID)"""
        result = self._request('POST', '/api/containers', {
            'image': image,
            'command': command
        })
        return result.get('container_id', '')
    
    def run(self, container_id: str, command: str) -> str:
        """Выполнить команду в контейнере (возвращает вывод)"""
        result = self._request('POST', f'/api/containers/{container_id}/exec', {
            'command': command
        })
        return result.get('output', '')
    
    def list_containers(self) -> List[Dict]:
        """Список контейнеров"""
        result = self._request('GET', '/api/containers')
        return result.get('containers', [])
    
    def delete(self, container_id: str) -> bool:
        """Удалить контейнер"""
        result = self._request('DELETE', f'/api/containers/{container_id}')
        return result.get('success', False)
    
    # === УДОБНЫЕ МЕТОДЫ ===
    
    def quick_run(self, command: str, image: str = "python:3.12") -> str:
        """Быстро создать контейнер, выполнить команду и удалить"""
        container_id = self.create(image)
        if not container_id:
            return "❌ Не удалось создать контейнер"
        
        try:
            output = self.run(container_id, command)
            return output
        finally:
            self.delete(container_id)
    
    def python(self, code: str) -> str:
        """Выполнить Python код"""
        return self.quick_run(f"python -c \"{code}\"")
    
    def shell(self, command: str) -> str:
        """Выполнить shell команду"""
        return self.quick_run(f"bash -c \"{command}\"")
    
    def file_create(self, container_id: str, filename: str, content: str) -> str:
        """Создать файл в контейнере"""
        return self.run(container_id, f"file create filename{{{filename}}}")
    
    def file_read(self, container_id: str, filename: str) -> str:
        """Прочитать файл из контейнера"""
        return self.run(container_id, f"file open filename{{{filename}}} as:readonly")
    
    def venv_create(self, container_id: str, name: str = "venv", version: str = "3.12.1") -> str:
        """Создать виртуальное окружение"""
        return self.run(container_id, f"venv {name}{{{version}}}")
    
    def venv_activate(self, container_id: str) -> str:
        """Активировать виртуальное окружение"""
        return self.run(container_id, "venv activate")
    
    def pip_install(self, container_id: str, package: str) -> str:
        """Установить пакет через localpip"""
        return self.run(container_id, f"localpip install {package}")
    
    def folder_create(self, container_id: str, name: str) -> str:
        """Создать папку"""
        return self.run(container_id, f"folder create foldername{{{name}}}")
    
    def folder_list(self, container_id: str, name: str = "") -> str:
        """Список файлов в папке"""
        if name:
            return self.run(container_id, f"folder list folder{{{name}}}")
        else:
            return self.run(container_id, "directory cdirectlist")
    
    # === КОНТЕКСТНЫЙ МЕНЕДЖЕР ===
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# === ГЛОБАЛЬНЫЕ ФУНКЦИИ ДЛЯ УДОБСТВА ===

def quick_python(code: str) -> str:
    """Быстро выполнить Python код"""
    with SimpleOpenIDE() as ide:
        return ide.python(code)

def quick_shell(command: str) -> str:
    """Быстро выполнить shell команду"""
    with SimpleOpenIDE() as ide:
        return ide.shell(command)

def quick_run(command: str) -> str:
    """Быстро выполнить команду"""
    with SimpleOpenIDE() as ide:
        return ide.quick_run(command)

# === ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ===

if __name__ == "__main__":
    # Простые примеры
    print("=== ПРОСТЫЕ ПРИМЕРЫ ===")
    
    # Быстрое выполнение Python
    result = quick_python("print('Привет из OpenIDE!')")
    print("Python:", result)
    
    # Быстрое выполнение shell
    result = quick_shell("echo 'Hello World'")
    print("Shell:", result)
    
    # Работа с контейнером
    print("\n=== РАБОТА С КОНТЕЙНЕРОМ ===")
    with SimpleOpenIDE() as ide:
        # Создаем контейнер
        container_id = ide.create()
        print(f"Создан контейнер: {container_id}")
        
        # Создаем файл
        ide.file_create(container_id, "test.py", "print('Hello from file!')")
        
        # Выполняем файл
        result = ide.run(container_id, "run: python{test.py}")
        print("Результат:", result)
        
        # Список файлов
        files = ide.folder_list(container_id)
        print("Файлы:", files)
