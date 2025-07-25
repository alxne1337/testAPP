import aiosqlite
from dotenv import load_dotenv
import os

load_dotenv()

async def init_db():
    async with aiosqlite.connect(os.getenv('DATABASE')) as db:
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

async def create_session():
    async with aiosqlite.connect(os.getenv('DATABASE')) as db:
        db.row_factory = aiosqlite.Row
        yield db

