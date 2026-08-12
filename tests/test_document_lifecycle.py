import os
import time


def test_upload_and_get_files_api(client, auth_user, create_kb):

    kb_name = create_kb()

    headers = auth_user["headers"]

    file = {
        "file": (
            "api_text.txt",
            "铜基复合材料是一种复合材料",
            "text/plain"
        )
    }

    data = {
        "kb_name": kb_name
    }

    upload_response = client.post(
        "/files",
        files=file,
        data=data,
        headers=headers
    )

    assert upload_response.status_code == 200

    task_id = upload_response.json()["data"]["task_id"]

    # 等待 Celery 完成
    for _ in range(30):
        response = client.get(
            f"/tasks/{task_id}",
            headers=headers
        )

        task = response.json()["data"]

        if task["status"] == "success":
            break

        if task["status"] == "failed":
            raise AssertionError(task.get("error_message"))

        time.sleep(0.5)

    else:
        raise AssertionError("Celery task timeout")

    response = client.get(
        "/files/files_message",
        params={
            "kb_name": kb_name
        },
        headers=headers
    )
    assert response.status_code == 200

    result = response.json()

    assert result["data"]["count"] == 1

    document = result["data"]["files"][0]

    assert document["filename"] == "api_text.txt"

    # 文件存在
    file_path = document["file_path"]

    assert os.path.exists(file_path)

    # 删除文档
    delete_response = client.delete(
        f"/files/{doc_id}",
        params={
            "kb_name": kb_name,
        },
        headers=headers
    )

    assert delete_response.status_code == 200

    files_response = client.get(
        "/files/files_message",
        params={
            "kb_name": kb_name
        },
        headers=headers
    )

    files = files_response.json()["data"]

    assert files["count"] == 0

    # 文件被删除
    assert not os.path.exists(file_path)


