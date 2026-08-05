from app.crud.chunk_crud import get_chunks_by_document_id


def test_chunk_upload_api(
        client,
        auth_user,
        create_kb,
        db
):

    kb_name = create_kb()

    file = {
        "file": (
            "chunk_test.txt",
            "铜基复合材料是...",
            "text/plain"
        )
    }

    headers = auth_user["headers"]

    data = {
        "kb_name": kb_name,
    }

    response = client.post(
        "/files/",
        files=file,
        data=data,
        headers=headers
    )

    assert response.status_code == 200

    result = response.json()

    doc_id = result["data"]["document_id"]

    chunks = get_chunks_by_document_id(
        db,
        doc_id,
    )
    assert len(chunks) > 0

    assert chunks[0].document_id == doc_id

    assert chunks[0].chunk_index == 0


def test_chunk_get_for_kb_api(
        client,
        auth_user,
        create_kb
):
    file = {
        "file": (
            "chunk_test.txt",
            "铜基复合材料的制备工艺决定了材料内部结构以及最终性能。目前常见制备方法包括粉末冶金法、搅拌铸造法、喷射沉积法以及原位生成法。粉末冶金法是制备铜基复合材料的重要方法之一。该方法首先将铜粉与增强相粉末进行混合，然后通过压制成型和烧结过程获得复合材料。粉末冶金具有增强相分布均匀、材料性能稳定等优点。搅拌铸造法是一种液态成型方法，通过机械搅拌使增强相均匀分散在熔融铜液中，然后进行浇注成型。该方法工艺简单，适合大规模生产。喷射沉积法利用高速气流将液态金属雾化，并使其与增强颗粒结合形成沉积坯。该方法可以减少偏析，提高材料组织均匀性。原位生成法是在材料制备过程中通过化学反应直接生成增强相，使增强相与铜基体结合更加紧密。",
            "text/plain"
        ),
    }
    kb_name = create_kb()

    data = {
        "kb_name": kb_name,
    }

    headers = auth_user["headers"]

    response = client.post(
        "/files/",
        files=file,
        data=data,
        headers=headers
    )

    assert response.status_code == 200

    result = client.get(
        "/files/files_message",
        params={
            "kb_name": kb_name
        },
        headers=headers
    )
    result = result.json()

    assert result["data"]["count"] == 1

    assert len(result["data"]["files"][0]["chunks"]) > 0


def test_chunk_delete_for_kb_api(
        auth_user,
        client,
        create_kb
):
    kb_name = create_kb()

    file = {
        "file": (
            "chunk_test.txt",
            "铜基复合材料的制备工艺决定了材料内部结构以及最终性能。目前常见制备方法包括粉末冶金法、搅拌铸造法、喷射沉积法以及原位生成法。粉末冶金法是制备铜基复合材料的重要方法之一。该方法首先将铜粉与增强相粉末进行混合，然后通过压制成型和烧结过程获得复合材料。粉末冶金具有增强相分布均匀、材料性能稳定等优点。搅拌铸造法是一种液态成型方法，通过机械搅拌使增强相均匀分散在熔融铜液中，然后进行浇注成型。该方法工艺简单，适合大规模生产。喷射沉积法利用高速气流将液态金属雾化，并使其与增强颗粒结合形成沉积坯。该方法可以减少偏析，提高材料组织均匀性。原位生成法是在材料制备过程中通过化学反应直接生成增强相，使增强相与铜基体结合更加紧密。",
            "text/plain"
        )
    }

    data = {
        "kb_name": kb_name,
    }

    headers = auth_user["headers"]

    response = client.post(
        "/files/",
        files=file,
        data=data,
        headers=headers
    )

    assert response.status_code == 200

    doc_id = response.json()["data"]["document_id"]

    delete_response = client.delete(
        f"/files/{doc_id}",
        params={
            "kb_name": kb_name
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

