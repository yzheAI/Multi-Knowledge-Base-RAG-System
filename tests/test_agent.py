from agent.agent import run_agent


def test_agent_knowledge_search(
        client,
        auth_user,
        create_kb
):
    kb_name = create_kb()

    response = client.post(
        "/agent/",
        params={
            "query": "MD32450是什么？",
            "kb_name": kb_name,
        },
        headers=auth_user["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, str)
    assert data


def test_agent_document_search(
        client,
        auth_user,
        create_kb
):
    kb_name = create_kb()

    response = client.post(
        "/agent/",
        params={
            "query": "找一下刀具相关文档",
            "kb_name": kb_name,
        },
        headers=auth_user["headers"]
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, str)
    assert data
