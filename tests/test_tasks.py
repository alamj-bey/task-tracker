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


def test_patch_explicit_null_title_rejected_422(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"title": None})
    assert r.status_code == 422


def test_patch_explicit_null_status_rejected_422(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"status": None})
    assert r.status_code == 422


def test_patch_omitted_title_leaves_it_unchanged(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"assignee": "Sam"})
    assert r.status_code == 200
    assert r.json()["title"] == created_task["title"]


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


def test_create_task_with_tags_returns_201_with_tags(client):
    r = client.post("/tasks", json={"title": "Tagged task", "tags": ["bug", "urgent"]})
    assert r.status_code == 201
    assert sorted(r.json()["tags"]) == ["bug", "urgent"]


def test_create_task_rejects_blank_tag_422(client):
    r = client.post("/tasks", json={"title": "Bad tags", "tags": ["ok", "   "]})
    assert r.status_code == 422


def test_create_task_rejects_too_many_tags_422(client):
    r = client.post("/tasks", json={"title": "Too many", "tags": ["a", "b", "c", "d", "e", "f"]})
    assert r.status_code == 422


def test_update_task_tags_replaces_list(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"tags": ["backend"]})
    assert r.status_code == 200
    assert r.json()["tags"] == ["backend"]


def test_update_task_tags_preserves_other_fields(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"tags": ["frontend"]})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == created_task["title"]
    assert body["tags"] == ["frontend"]


def test_filter_tasks_by_tag_returns_only_matches(client):
    client.post("/tasks", json={"title": "A", "tags": ["bug"]})
    client.post("/tasks", json={"title": "B", "tags": ["feature"]})
    r = client.get("/tasks", params={"tag": "bug"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["A"]


def test_filter_tasks_by_tag_no_match_returns_200_empty_list(client, created_task):
    r = client.get("/tasks", params={"tag": "nonexistent"})
    assert r.status_code == 200
    assert r.json() == []


def test_filter_tasks_by_tag_case_insensitive(client):
    client.post("/tasks", json={"title": "A", "tags": ["Bug"]})
    r = client.get("/tasks", params={"tag": "bug"})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_filter_tasks_by_tag_partial_match(client):
    client.post("/tasks", json={"title": "A", "tags": ["docs"]})
    r = client.get("/tasks", params={"tag": "doc"})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_search_matches_title_case_insensitive(client):
    client.post("/tasks", json={"title": "Fix login bug"})
    client.post("/tasks", json={"title": "Write docs"})
    r = client.get("/tasks", params={"search": "LOGIN"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["Fix login bug"]


def test_search_matches_description(client):
    client.post("/tasks", json={"title": "Task A", "description": "involves the payment gateway"})
    client.post("/tasks", json={"title": "Task B", "description": "unrelated"})
    r = client.get("/tasks", params={"search": "payment"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["Task A"]


def test_search_no_match_returns_200_empty_list(client, created_task):
    r = client.get("/tasks", params={"search": "zzz_no_match"})
    assert r.status_code == 200
    assert r.json() == []


def test_search_combined_with_status_and_priority(client):
    client.post("/tasks", json={"title": "Login fix", "priority": "High"})
    client.post("/tasks", json={"title": "Login docs", "priority": "Low"})
    r = client.get("/tasks", params={"search": "login", "priority": "High"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["Login fix"]


def test_search_combined_with_tag_filter(client):
    client.post("/tasks", json={"title": "Login fix", "tags": ["bug"]})
    client.post("/tasks", json={"title": "Login docs", "tags": ["docs"]})
    r = client.get("/tasks", params={"search": "login", "tag": "bug"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["Login fix"]


def test_invalid_status_filter_returns_422(client):
    r = client.get("/tasks", params={"status": "NotARealStatus"})
    assert r.status_code == 422


def test_combined_filters_use_and_logic_not_or(client):
    client.post("/tasks", json={"title": "Match all", "priority": "High", "tags": ["bug"]})
    client.post("/tasks", json={"title": "Only priority matches", "priority": "High", "tags": ["docs"]})
    client.post("/tasks", json={"title": "Only tag matches", "priority": "Low", "tags": ["bug"]})
    r = client.get("/tasks", params={"priority": "High", "tag": "bug"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["Match all"]
