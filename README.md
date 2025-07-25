# FastAPI Task Management Application

## Описание

Проект представляет собой REST API для управления задачами, построенный на FastAPI с использованием SQLite в качестве базы данных. Приложение поддерживает основные CRUD-операции и фильтрацию задач по статусу.

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.11+
- Docker (опционально)
- Docker Compose (опционально)

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/task-management-api.git
cd task-management-api
```
2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```
3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### Запуск приложения
Локальный запуск приложения
```bash
uvicorn src.main:app --reload
```
Приложение будет доступно по адресу: http://localhost:8000

Локальный запуск тестов
```bash
pytest tests/
```

Запуск через Docker
```bash
docker-compose build
docker-compose up app
```

Запуск тестов через Docker
```bash
docker-compose up tests
```

### Документация API

Swagger UI: http://localhost:8000/docs

### Окружение

Если производится локальный запуск то требуется создать файл .env с параметрами: 
    DATABASE = 'tasks.db'
    TEST_DB = 'tests/tasks.db'