import aiosqlite
from fastapi import Depends, HTTPException, status
from src.database.core import create_session
from src.database.entities import CreateTask, TaskResponce, TaskUpdate, TaskStatus
from datetime import datetime, timezone


async def create_task(new_task: CreateTask, db: aiosqlite.Connection = Depends(create_session)):
    async with db.cursor() as cursor:
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await cursor.execute(
            """INSERT INTO tasks (name, description, status, created_at)
                VALUES (?, ?, ?, ?)""",
                (new_task.name, new_task.description, new_task.status.value, created_at)
            )
        
        await db.commit()

        task_id = cursor.lastrowid
        await cursor.execute(
            "SELECT * FROM tasks WHERE id = ?", 
            (task_id,)
        )
        task_data = await cursor.fetchone()

        if task_data:
            return dict(task_data)
        
        raise HTTPException(status_code=404, detail="При создании задачи произошла ошибка!")
    
async def filter_status(param:str, db: aiosqlite.Connection = Depends(create_session)):
    async with db.cursor() as cursor:
        if param == None:
            await cursor.execute("SELECT * FROM tasks")
        else:
            await cursor.execute(
                "SELECT * FROM tasks WHERE status == ?",
                (param,)
            )
        tasks = await cursor.fetchall()
        return tasks
    
async def update_task(task_id: int, task: TaskUpdate, db: aiosqlite.Connection = Depends(create_session)):
    async with db.cursor() as cursor:

        update_fields = {}

        if task.name is not None:
            update_fields['name'] = task.name
        if task.description is not None:
            update_fields['description'] = task.description
        if task.status is not None:
            update_fields['status'] = task.status.value
        
        if not update_fields:
            raise HTTPException(
                status_code=400,
                detail="Вы не внесли ни одного изменения!"
            )
        
        set_clause = ", ".join(f"{field} = ?" for field in update_fields)
        values = list(update_fields.values())
        values.append(task_id)

        await cursor.execute(
            f"""UPDATE tasks
            SET {set_clause}
            WHERE id = ?""",
            values
        )
        await db.commit()

        await cursor.execute(
            "SELECT id, name, description, status, created_at FROM tasks WHERE id = ?",
            (task_id,)
        )
        task_data = await cursor.fetchone()
        
        if not task_data:
            raise HTTPException(
                status_code=404,
                detail="Задача не найдена"
            )
        
        return dict(task_data)
    
async def delete_task(task_id: int, db: aiosqlite.Connection):
    async with db.cursor() as cursor:
        await cursor.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,)
        )
        task_exists = await cursor.fetchone()
        
        if not task_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Задача {task_id} не найдена"
            )
        
        await cursor.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )
        await db.commit()
        
        return {
            "status": "success",
            "message": f"Задача {task_id} успешно удалена"
        }