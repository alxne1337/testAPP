from fastapi import APIRouter, Depends
from src.database.core import create_session
from aiosqlite import Connection
from src.database.entities import CreateTask, TaskResponce, TaskUpdate
from src.tasks.view import create_task, filter_status, update_task, delete_task
from typing import List

router = APIRouter(prefix='/tasks', tags = ['tasks'])

@router.post('/create', response_model=TaskResponce)
async def create(task: CreateTask, db: Connection = Depends(create_session)):
    new_task = await create_task(task, db)
    return new_task

@router.get('/filter', response_model=List[TaskResponce])
async def task_filter(param: str = None, db: Connection = Depends(create_session)):
    tasks = await filter_status(param, db)
    return [dict(task) for task in tasks]

@router.patch('/{task_id}', response_model= TaskResponce)
async def task_update(id: int, update_data: TaskUpdate, db: Connection = Depends(create_session)):
    updated_task = await update_task(id, update_data, db)
    return updated_task

@router.delete('/{task_id}')
async def delete(task_id: int, db: Connection = Depends(create_session)):
    return await delete_task(task_id, db)