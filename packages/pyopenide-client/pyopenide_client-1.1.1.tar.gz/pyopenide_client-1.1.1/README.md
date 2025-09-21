# 🚀 PyOpenIDE Client

**Упрощенные клиенты для OpenIDE с разными уровнями простоты синтаксиса**

PyOpenIDE Client - это коллекция упрощенных клиентов для работы с OpenIDE API, которые делают написание кода максимально простым и удобным.

## ✨ Особенности

- 🎯 **5 уровней сложности** - от ультра-простого до профессионального
- 🚀 **Быстрый старт** - импортируй и используй
- 🔧 **Все команды OpenIDE** - полная поддержка всех функций
- 🐍 **Python-синтаксис** - знакомый и понятный код
- 📦 **Автоматическое управление** - контейнеры создаются и удаляются автоматически
- 🌐 **HTTP API** - работает через REST API

## 📦 Установка

```bash
pip install pyopenide-client
```

## 🎯 Быстрый старт

### Ультра-простой синтаксис (рекомендуется для начинающих)

```python
from pyopenide_client import *

# Просто импортируй и используй!
print(py("print('Привет OpenIDE!')"))
print(sh("echo 'Hello World'"))
print(pwd())
print(whoami())

# Работа с файлами
file_create("test.py", "print('Hello from file!')")
content = file_read("test.py")
result = run_python("test.py")

# Виртуальные окружения
venv_create("myenv")
venv_activate()
pip_install("requests")
packages = pip_list()

# Системные команды
print(date())
print(uptime())
print(free())
print(ps())
```

### Магический синтаксис (для опытных)

```python
from pyopenide_client import ide

# Создаем клиент
o = ide()

# Простые команды
print(o("ls -la"))
print(o("pwd"))

# Python код
print(o.python("print('Hello!')"))
print(o.python("print(2 + 2 * 3)"))

# Работа с файлами
o.file.create("test.py", "print('Hello from file!')")
content = o.file.read("test.py")
result = o.run("python{test.py}")

# Контекстный менеджер
with ide() as i:
    print(i("whoami"))
    print(i.python("import sys; print(sys.version)"))
```

### Простой синтаксис (для профессионалов)

```python
from pyopenide_client import SimpleOpenIDE

# Создаем клиент
ide = SimpleOpenIDE()

# Быстрое выполнение
result = ide.quick_run("ls -la")
print(result)

# Python код
result = ide.python("print('Hello!')")
print(result)

# Работа с контейнером
container_id = ide.create()
ide.file_create(container_id, "test.py", "print('Hello!')")
result = ide.run(container_id, "run: python{test.py}")
print(result)
ide.delete(container_id)
```

## 📚 Уровни сложности

| Уровень | Файл | Синтаксис | Пример |
|---------|------|-----------|--------|
| 🟢 **Ультра-простой** | `ultra_simple` | `py("code")` | `py("print('hello')")` |
| 🟡 **Глобальный** | `global_client` | `py("code")` | `py("print('hello')")` |
| 🟠 **Магический** | `magic_client` | `o.python("code")` | `o.python("print('hello')")` |
| 🔴 **Декораторный** | `decorator_client` | `python("code")` | `python("print('hello')")` |
| ⚫ **Простой** | `simple_client` | `ide.python("code")` | `ide.python("print('hello')")` |

## 🎨 Примеры использования

### 1. Ультра-простой синтаксис

```python
from pyopenide_client import *

# Python код
print(py("print('Привет OpenIDE!')"))
print(py("print(2 + 2 * 3)"))

# Shell команды
print(sh("echo 'Hello World'"))
print(sh("ls -la"))

# Системные команды
print(pwd())
print(whoami())
print(date())
print(uptime())

# Работа с файлами
file_create("hello.py", "print('Hello from file!')")
content = file_read("hello.py")
result = run_python("hello.py")

# Список файлов
files = ls()
print(files)

# Виртуальные окружения
venv_create("myenv")
venv_activate()
pip_install("requests")
packages = pip_list()
```

### 2. Магический синтаксис

```python
from pyopenide_client import ide

# Создаем клиент
o = ide()

# Простые команды
print(o("ls -la"))
print(o("pwd"))

# Python код
print(o.python("print('Hello!')"))
print(o.python("print(2 + 2 * 3)"))

# Shell команды
print(o.shell("echo 'Hello World'"))
print(o.shell("date"))

# Работа с файлами
o.file.create("test.py", "print('Hello from file!')")
content = o.file.read("test.py")
result = o.run("python{test.py}")

# Работа с папками
o.folder.create("mydir")
files = o.folder.list("mydir")

# Контекстный менеджер
with ide() as i:
    print(i("whoami"))
    print(i.python("import sys; print(sys.version)"))
```

### 3. Декораторный синтаксис

```python
from pyopenide_client import openide, python, shell, run

# Простые функции
print(python("print('Hello!')"))
print(shell("echo 'Hello World'"))
print(run("ls -la"))

# Декораторы
@openide
def hello():
    return "echo 'Hello from decorator!'"

@openide
def math_calc():
    return "python -c \"print(2 + 2 * 3)\""

print(hello())
print(math_calc())
```

### 4. Простой синтаксис

```python
from pyopenide_client import SimpleOpenIDE

# Создаем клиент
ide = SimpleOpenIDE()

# Быстрое выполнение
result = ide.quick_run("ls -la")
print(result)

# Python код
result = ide.python("print('Hello!')")
print(result)

# Работа с контейнером
container_id = ide.create()
ide.file_create(container_id, "test.py", "print('Hello!')")
result = ide.run(container_id, "run: python{test.py}")
print(result)
ide.delete(container_id)
```

## 🔧 Доступные функции

### Python и Shell
- `py(code)` - выполнить Python код
- `sh(command)` - выполнить shell команду
- `cmd(command)` - выполнить команду
- `run_python(script)` - запустить Python скрипт
- `run_shell(command)` - запустить shell команду

### Файлы
- `file_create(filename, content)` - создать файл
- `file_read(filename)` - прочитать файл
- `file_delete(filename)` - удалить файл
- `cat(filename)` - показать содержимое файла
- `touch(filename)` - создать пустой файл
- `rm(filename)` - удалить файл
- `cp(source, target)` - копировать файл
- `mv(source, target)` - переместить файл

### Папки
- `folder_create(name)` - создать папку
- `folder_list(name)` - список файлов в папке
- `ls(path)` - список файлов
- `mkdir(name)` - создать директорию
- `rmdir(name)` - удалить директорию

### Виртуальные окружения
- `venv_create(name, version)` - создать виртуальное окружение
- `venv_activate()` - активировать виртуальное окружение
- `pip_install(package)` - установить пакет
- `pip_list()` - список пакетов

### Системные команды
- `pwd()` - текущая директория
- `whoami()` - текущий пользователь
- `date()` - текущая дата
- `uptime()` - время работы
- `ps()` - список процессов
- `top()` - топ процессов
- `df()` - использование диска
- `free()` - использование памяти
- `uname()` - информация о системе
- `env()` - переменные окружения

### Поиск и утилиты
- `grep(pattern, filename)` - поиск в файле
- `find(name)` - поиск файлов
- `which(command)` - путь к команде
- `whereis(command)` - где находится команда
- `man(command)` - справка по команде
- `help()` - справка OpenIDE
- `version()` - версия OpenIDE
- `clear()` - очистить экран

## 🚀 Требования

- Python 3.7+
- requests
- OpenIDE API сервер запущен на `http://127.0.0.1:5000`

## 📖 Документация

- [Полная документация](https://pypi.org/project/pyopenide-client/)
- [Примеры использования](https://github.com/openide/pyopenide-client/examples)
- [API Reference](https://github.com/openide/pyopenide-client/docs)

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие PyOpenIDE Client! Пожалуйста, ознакомьтесь с [руководством по вкладу](https://github.com/openide/pyopenide-client/CONTRIBUTING.md).

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](https://github.com/openide/pyopenide-client/LICENSE) для получения дополнительной информации.

## 🆘 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [FAQ](https://github.com/openide/pyopenide-client/FAQ.md)
2. Создайте [Issue](https://github.com/openide/pyopenide-client/issues)
3. Свяжитесь с нами: openide@example.com

## 🎯 Рекомендации

- **Для быстрого прототипирования:** используйте ультра-простой синтаксис
- **Для скриптов:** используйте глобальные функции
- **Для интерактивной работы:** используйте магический синтаксис
- **Для больших проектов:** используйте простой синтаксис

---

**Сделано с ❤️ командой OpenIDE**
