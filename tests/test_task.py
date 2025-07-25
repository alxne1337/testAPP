import pytest
from datetime import datetime
from fastapi import HTTPException
from src.database.entities import CreateTask, TaskResponce, TaskStatus, TaskUpdate

@pytest.mark.asyncio
async def test_database_isolation(db_session):
    from src.tasks.view import create_task

    cursor = await db_session.execute("SELECT COUNT(*) FROM tasks")
    count = (await cursor.fetchone())[0]
    assert count == 0

    task_data = CreateTask(name="Isolation Test")
    await create_task(task_data, db_session)

    cursor = await db_session.execute("SELECT COUNT(*) FROM tasks")
    count = (await cursor.fetchone())[0]
    assert count == 1


@pytest.mark.parametrize("name,description,status", [
    ("Test", "Desc", TaskStatus.PENDING),
    ("Minimal", None, TaskStatus.PENDING),
])
def test_task_models(name, description, status):
    task = CreateTask(name=name, description=description, status=status)
    assert task.name == name
    assert task.description == description
    assert task.status == status

    update_data = TaskUpdate(name="Updated", status=TaskStatus.IN_PROGRESS)
    assert update_data.name == "Updated"
    assert update_data.status == TaskStatus.IN_PROGRESS
    assert update_data.description is None


def test_task_response_model():
    sample_data = {
        "id": 1,
        "name": "Test",
        "description": "Desc",
        "status": "pending",
        "created_at": "2023-01-01 12:00:00"
    }

    task = TaskResponce(**sample_data)
    assert task.id == 1
    assert isinstance(task.created_at, datetime)
    assert task.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_create_task(db_session):
    from src.tasks.view import create_task

    task_data = CreateTask(name="Test", description="Desc")
    result = await create_task(task_data, db_session)

    assert result["name"] == "Test"
    assert result["description"] == "Desc"
    assert result["status"] == "pending"
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
@pytest.mark.parametrize("status,expected_count", [
    (None, 2),
    ("pending", 1),
    ("in_progress", 1),
    ("done", 0)
])
async def test_filter_status(db_session, status, expected_count):
    from src.tasks.view import filter_status, create_task

    await create_task(CreateTask(name="Task 1", status=TaskStatus.PENDING), db_session)
    await create_task(CreateTask(name="Task 2", status=TaskStatus.IN_PROGRESS), db_session)

    filtered_tasks = await filter_status(status, db_session)
    assert len(filtered_tasks) == expected_count
    if status:
        assert all(task["status"] == status for task in filtered_tasks)


@pytest.mark.asyncio
async def test_update_task(db_session):
    from src.tasks.view import update_task, create_task

    task_data = CreateTask(name="Original", description="Original Desc")
    created_task = await create_task(task_data, db_session)
    task_id = created_task["id"]

    update_data = TaskUpdate(name="Updated", status=TaskStatus.DONE)
    updated_task = await update_task(task_id, update_data, db_session)
    assert updated_task["name"] == "Updated"
    assert updated_task["status"] == "done"
    assert updated_task["description"] == "Original Desc"

    update_data = TaskUpdate(description="New Desc")
    updated_task = await update_task(task_id, update_data, db_session)
    assert updated_task["name"] == "Updated"  # Осталось прежним
    assert updated_task["description"] == "New Desc"

    with pytest.raises(HTTPException) as exc_info:
        await update_task(task_id, TaskUpdate(), db_session)
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info:
        await update_task(9999, update_data, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(db_session):
    from src.tasks.view import delete_task, create_task

    task_data = CreateTask(name="To Delete")
    created_task = await create_task(task_data, db_session)
    task_id = created_task["id"]

    result = await delete_task(task_id, db_session)
    assert result["status"] == "success"

    with pytest.raises(HTTPException) as exc_info:
        await delete_task(task_id, db_session)
    assert exc_info.value.status_code == 404

    with pytest.raises(HTTPException) as exc_info:
        await delete_task(9999, db_session)
    assert exc_info.value.status_code == 404


def test_api_endpoints(client):
    
    task_data = {
        "name": "API Test Task",
        "description": "API Test Description",
        "status": "in_progress"
    }

    response = client.post("/tasks/create", json=task_data)
    assert response.status_code == 200
    created_task = response.json()
    assert created_task["name"] == "API Test Task"
    assert created_task["status"] == "in_progress"
    task_id = created_task["id"]

    response = client.get("/tasks/filter")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert any(t["id"] == task_id for t in tasks)

    update_data = {
        "name": "Updated via API",
        "description": "testing",
        "status": "done"
    }
    
    from src.database.entities import TaskUpdate
    update_model = TaskUpdate(**update_data)
    response = client.patch(f"/tasks/{task_id}", json=update_model.dict())

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    response = client.get("/tasks/filter")
    assert all(task["id"] != task_id for task in response.json())