def test_health_returns_200(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_task_valid_returns_201(client):
    r = client.post("/tasks", json={"title": "Write report"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Write report"
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"


def test_create_task_missing_title_returns_422(client):
    r = client.post("/tasks", json={})
    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client):
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    r = client.post("/tasks", json={"title": "Valid", "nonexistent_field": "x"})
    assert r.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_empty(client, created_task):
    r = client.get("/tasks", params={"status": "Done"})
    assert r.status_code == 200
    assert r.json() == []


def test_get_task_by_id_returns_task(client, created_task):
    r = client.get(f"/tasks/{created_task['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created_task["id"]


def test_get_task_by_id_not_found_returns_404(client):
    r = client.get("/tasks/does-not-exist")
    assert r.status_code == 404


def test_patch_partial_update_keeps_other_fields(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"assignee": "Alex"})
    assert r.status_code == 200
    body = r.json()
    assert body["assignee"] == "Alex"
    assert body["title"] == created_task["title"]


def test_patch_not_found_returns_404(client):
    r = client.patch("/tasks/does-not-exist", json={"assignee": "Alex"})
    assert r.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
    assert r.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert r.status_code == 422


def test_delete_existing_returns_204_no_body(client, created_task):
    r = client.delete(f"/tasks/{created_task['id']}")
    assert r.status_code == 204
    assert r.content == b""


def test_delete_missing_returns_404(client):
    r = client.delete("/tasks/does-not-exist")
    assert r.status_code == 404
