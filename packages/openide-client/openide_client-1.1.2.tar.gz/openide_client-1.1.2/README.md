# OpenIDE Client

Python клиентская библиотека для работы с OpenIDE контейнерной системой через HTTP API.

## 🚀 Установка

```bash
pip install openide-client
```

## 📖 Быстрый старт

### Базовое использование

```python
from openide_client import create_api_client

# Создание клиента
client = create_api_client("127.0.0.1", 5000)

# Проверка здоровья API
health = client.health_check()
print(f"API статус: {health['status']}")

# Создание контейнера
result = client.create_container("python:3.12", "bash")
container_id = result['container_id']
print(f"Контейнер создан: {container_id}")

# Выполнение команды
output = client.exec_command(container_id, "ls -la")
print(f"Результат: {output['output']}")

# Удаление контейнера
client.delete_container(container_id)
```

### Использование CLI

```bash
# Проверка здоровья API
openide-client health

# Список контейнеров
openide-client containers

# Создание контейнера
openide-client create python:3.12 bash

# Выполнение команды
openide-client exec <container_id> "ls -la"

# Удаление контейнера
openide-client delete <container_id>
```

## 🔧 API Reference

### OpenIDEAPIClient

#### Методы

- `health_check()` - Проверка здоровья API
- `list_containers()` - Получение списка контейнеров
- `create_container(image, command)` - Создание контейнера
- `get_container_info(container_id)` - Информация о контейнере
- `execute_command_in_container(container_id, command)` - Выполнение команды
- `delete_container(container_id)` - Удаление контейнера

#### Примеры

```python
from openide_client import OpenIDEAPIClient, OpenIDEConfig

# Создание конфигурации
config = OpenIDEConfig(
    api_key="your-api-key",
    base_url="http://127.0.0.1:5000"
)

# Создание клиента
client = OpenIDEAPIClient(config)

# Работа с контейнерами
containers = client.list_containers()
print(f"Найдено контейнеров: {len(containers['containers'])}")

# Создание Python контейнера
result = client.create_container("python:3.12", "bash")
container_id = result['container_id']

# Установка пакетов
client.exec_command(container_id, "pip install requests")

# Запуск Python скрипта
output = client.exec_command(container_id, "python -c 'import requests; print(requests.__version__)'")
print(output['output'])
```

## 🐳 Поддерживаемые образы

- `python:3.12` - Python 3.12
- `python:3.11` - Python 3.11
- `python:3.10` - Python 3.10
- `node:18` - Node.js 18
- `node:20` - Node.js 20
- `ubuntu:22.04` - Ubuntu 22.04
- `alpine:3.18` - Alpine Linux

## 🔐 Безопасность

- Все контейнеры изолированы в chroot jail
- Ограничен доступ к родительским директориям
- Автоматическое управление ресурсами (RAM, CPU)
- Временные контейнеры с автоочисткой

## 📝 Примеры использования

### Разработка Python приложений

```python
# Создание Python окружения
result = client.create_container("python:3.12", "bash")
container_id = result['container_id']

# Установка зависимостей
client.exec_command(container_id, "pip install flask requests")

# Создание файла
client.exec_command(container_id, "echo 'from flask import Flask\napp = Flask(__name__)\n@app.route(\"/\")\ndef hello():\n    return \"Hello OpenIDE!\"\n\nif __name__ == \"__main__\":\n    app.run(host=\"0.0.0.0\", port=5000)' > app.py")

# Запуск приложения
output = client.exec_command(container_id, "python app.py")
```

### Тестирование Node.js приложений

```python
# Создание Node.js окружения
result = client.create_container("node:18", "bash")
container_id = result['container_id']

# Инициализация проекта
client.exec_command(container_id, "npm init -y")

# Установка зависимостей
client.exec_command(container_id, "npm install express")

# Создание сервера
client.exec_command(container_id, "echo 'const express = require(\"express\");\nconst app = express();\napp.get(\"/\", (req, res) => res.send(\"Hello OpenIDE!\"));\napp.listen(3000, () => console.log(\"Server running on port 3000\"));' > server.js")

# Запуск сервера
output = client.exec_command(container_id, "node server.js")
```

## 🛠️ Конфигурация

### Переменные окружения

```bash
export OPENIDE_API_KEY="your-api-key"
export OPENIDE_BASE_URL="http://127.0.0.1:5000"
export OPENIDE_TIMEOUT="30"
```

### Конфигурационный файл

```python
from openide_client import OpenIDEConfig

config = OpenIDEConfig(
    api_key="your-api-key",
    base_url="http://127.0.0.1:5000",
    timeout=30,
    verify_ssl=True
)
```

## 🐛 Обработка ошибок

```python
from openide_client import OpenIDEAPIClient, OpenIDEConfig

try:
    client = OpenIDEAPIClient(OpenIDEConfig(api_key="test"))
    result = client.create_container("python:3.12", "bash")
    print(f"Успех: {result}")
except Exception as e:
    print(f"Ошибка: {e}")
```

## 📚 Дополнительные ресурсы

- [OpenIDE GitHub](https://github.com/artemjs/OpenIDE/tree/openide-client)
- [PyPI страница](https://pypi.org/project/openide-client/)
- [Документация API](https://pypi.org/project/openide-client/1.1.2/)

## 🤝 Поддержка

Если у вас есть вопросы или проблемы:

1. Создайте issue на GitHub
2. Напишите на email: artemjson@gmail.com
3. Проверьте документацию API

## 📄 Лицензия

MIT License - см. файл LICENSE для подробностей.
