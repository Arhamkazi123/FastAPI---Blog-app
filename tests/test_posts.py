def test_create_post(client, auth_headers):
    """Logged-in user can create a post"""
    response = client.post("/posts/", json={
        "title": "My first post",
        "content": "Hello world",
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My first post"
    assert data["content"] == "Hello world"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_create_post_without_auth(client):
    """Unauthenticated user cannot create a post"""
    response = client.post("/posts/", json={
        "title": "Sneaky post",
        "content": "Should fail",
    })
    assert response.status_code == 401


def test_get_posts(client, auth_headers):
    """List posts returns created posts"""
    # Create two posts
    client.post("/posts/", json={"title": "Post 1", "content": "Content 1"}, headers=auth_headers)
    client.post("/posts/", json={"title": "Post 2", "content": "Content 2"}, headers=auth_headers)

    # Get all posts (no auth needed)
    response = client.get("/posts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_posts_pagination(client, auth_headers):
    """Pagination returns correct number of posts"""
    # Create 5 posts
    for i in range(5):
        client.post("/posts/", json={"title": f"Post {i}", "content": f"Content {i}"}, headers=auth_headers)

    # Get first page with limit 2
    response = client.get("/posts/?page=1&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Get second page
    response = client.get("/posts/?page=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Get third page — only 1 post left
    response = client.get("/posts/?page=3&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_single_post(client, auth_headers):
    """Get a post by id"""
    create_response = client.post("/posts/", json={"title": "Solo post", "content": "Just me"}, headers=auth_headers)
    post_id = create_response.json()["id"]

    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Solo post"


def test_get_nonexistent_post(client):
    """Getting a post that doesn't exist returns 404"""
    response = client.get("/posts/9999")
    assert response.status_code == 404


def test_update_own_post(client, auth_headers):
    """User can update their own post"""
    create_response = client.post("/posts/", json={"title": "Old title", "content": "Old content"}, headers=auth_headers)
    post_id = create_response.json()["id"]

    response = client.put(f"/posts/{post_id}", json={"title": "New title", "content": "New content"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["content"] == "New content"


def test_update_other_users_post(client, auth_headers):
    """User cannot update someone else's post"""
    # testuser creates a post
    create_response = client.post("/posts/", json={"title": "My post", "content": "Mine"}, headers=auth_headers)
    post_id = create_response.json()["id"]

    # Register and login as a different user
    client.post("/auth/register", json={"username": "other", "password": "otherpass123"})
    login_response = client.post("/auth/login", json={"username": "other", "password": "otherpass123"})
    other_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    # Try to update testuser's post
    response = client.put(f"/posts/{post_id}", json={"title": "Hacked", "content": "Hacked"}, headers=other_headers)
    assert response.status_code == 403


def test_delete_own_post(client, auth_headers):
    """User can delete their own post"""
    create_response = client.post("/posts/", json={"title": "Delete me", "content": "Bye"}, headers=auth_headers)
    post_id = create_response.json()["id"]

    response = client.delete(f"/posts/{post_id}", headers=auth_headers)
    assert response.status_code == 204

    # Confirm it's gone
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 404


def test_delete_other_users_post(client, auth_headers):
    """Regular user cannot delete someone else's post"""
    create_response = client.post("/posts/", json={"title": "My post", "content": "Mine"}, headers=auth_headers)
    post_id = create_response.json()["id"]

    client.post("/auth/register", json={"username": "other", "password": "otherpass123"})
    login_response = client.post("/auth/login", json={"username": "other", "password": "otherpass123"})
    other_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    response = client.delete(f"/posts/{post_id}", headers=other_headers)
    assert response.status_code == 403
