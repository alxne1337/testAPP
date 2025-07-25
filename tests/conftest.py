import pytest
import pytest_asyncio
import aiosqlite
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from src.main import app
from src.database.core import init_db, create_session

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def test_db_path():
    path = os.getenv('TEST_DB')
    if os.path.exists(path):
        os.remove(path)
    return path


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db(test_db_path):
    async with aiosqlite.connect(test_db_path) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        await db.commit()


@pytest_asyncio.fixture
async def db_session(test_db_path):
    async with aiosqlite.connect(test_db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db
        await db.execute("DELETE FROM tasks")
        await db.commit()


@pytest_asyncio.fixture
async def clean_db():
    async with aiosqlite.connect(os.getenv('TEST_DB')) as db:
        await db.execute("DELETE FROM tasks")
        await db.commit()
    return os.getenv('TEST_DB')


@pytest.fixture
def client(db_session):
    app.dependency_overrides[create_session] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_task(client):
    task_data = {
        "name": "Test Task",
        "description": "Test Description",
        "status": "pending"
    }
    response = client.post("/tasks/create", json=task_data)
    return response.json()
