import uuid


def create_task(
    client,
    headers
):
    task_id = f"{uuid.uuid4().hex}"
    filename = f"filename_{task_id}"
    response = client.post(
        '/tasks/create',
        headers=headers,
        json={
            "task_id": task_id,
            "filename": filename,
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "pending"
    return task_id


def test_get_task(
        client,
        auth_user
):
    task_id = create_task(
        client,
        auth_user["headers"]
    )
    response = client.get(
        f"/tasks/{task_id}",
        headers=auth_user["headers"],
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "pending"
    assert result["task_id"] == task_id


def test_user_cannot_get_other_tasks(
        client,
        auth_user,
        auth_user_2
):
    user_header = auth_user["headers"]
    user_header2 = auth_user_2["headers"]
    task_id = create_task(
        client,
        user_header
    )
    response = client.get(
        f"/tasks/{task_id}",
        headers=user_header2,
    )
    assert response.status_code == 404


def test_get_all_task(
        client,
        auth_user,
):
    task_id_1 = create_task(
        client,
        auth_user["headers"]
    )
    task_id_2 = create_task(
        client,
        auth_user["headers"]
    )

    response = client.get(
        "/tasks/tasks",
        headers=auth_user["headers"],
    )
    task_ids = [
        task["task_id"]
        for task in response.json()["data"]
    ]
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert task_id_1 in task_ids
    assert task_id_2 in task_ids


def test_delete_task(
        client,
        auth_user,
):
    headers = auth_user["headers"]
    task_id = create_task(
        client,
        headers
    )

    response = client.delete(
        f"/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["task_id"] == task_id

    response = client.get(
        f"/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 404


def test_user_cannot_delete_other_tasks(
        client,
        auth_user,
        auth_user_2
):
    user_header_1 = auth_user["headers"]
    user_header_2 = auth_user_2["headers"]

    task_id = create_task(
        client,
        user_header_1
    )
    response = client.delete(
        f"/tasks/{task_id}",
        headers=user_header_2,
    )

    assert response.status_code == 404

    response = client.get(
        f"/tasks/{task_id}",
        headers=user_header_1,
    )
    assert response.status_code == 200
