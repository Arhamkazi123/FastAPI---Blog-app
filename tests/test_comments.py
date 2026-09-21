def test_create_comment(client, auth_headers):
    """Logged-in user can comment on a post"""
    # Create a post first
    post_response = client.post("/posts/", json={"title": "A post", "content": "Some content"}, headers=auth_headers)
    post_id = post_response.json()["id"]

    # Comment on it
    response = client.post(f"/posts/{post_id}/comments", json={"text": "Nice post!"}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Nice post!"
    assert data["post_id"] == post_id
    assert "user_id" in data
    assert "created_at" in data


def test_create_comment_without_auth(client, auth_headers):
    """Unauthenticated user cannot comment"""
    post_response = client.post("/posts/", json={"title": "A post", "content": "Content"}, headers=auth_headers)
    post_id = post_response.json()["id"]

    response = client.post(f"/posts/{post_id}/comments", json={"text": "Sneaky comment"})
    assert response.status_code == 401


def test_create_comment_on_nonexistent_post(client, auth_headers):
    """Commenting on a post that doesn't exist returns 404"""
    response = client.post("/posts/9999/comments", json={"text": "Hello?"}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_get_comments(client, auth_headers):
    """List comments for a post"""
    post_response = client.post("/posts/", json={"title": "A post", "content": "Content"}, headers=auth_headers)
    post_id = post_response.json()["id"]

    # Add two comments
    client.post(f"/posts/{post_id}/comments", json={"text": "Comment 1"}, headers=auth_headers)
    client.post(f"/posts/{post_id}/comments", json={"text": "Comment 2"}, headers=auth_headers)

    response = client.get(f"/posts/{post_id}/comments")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_comments_empty(client, auth_headers):
    """Post with no comments returns empty list"""
    post_response = client.post("/posts/", json={"title": "Lonely post", "content": "No comments"}, headers=auth_headers)
    post_id = post_response.json()["id"]

    response = client.get(f"/posts/{post_id}/comments")
    assert response.status_code == 200
    assert response.json() == []


def test_delete_own_comment(client, auth_headers):
    """User can delete their own comment"""
    post_response = client.post("/posts/", json={"title": "A post", "content": "Content"}, headers=auth_headers)
    post_id = post_response.json()["id"]

    comment_response = client.post(f"/posts/{post_id}/comments", json={"text": "Delete me"}, headers=auth_headers)
    comment_id = comment_response.json()["id"]

    response = client.delete(f"/comments/{comment_id}", headers=auth_headers)
    assert response.status_code == 204

    # Confirm it's gone
    response = client.get(f"/posts/{post_id}/comments")
    assert response.json() == []


def test_delete_other_users_comment(client, auth_headers):
    """Regular user cannot delete someone else's comment"""
    # testuser creates post and comment
    post_response = client.post("/posts/", json={"title": "A post", "content": "Content"}, headers=auth_headers)
    post_id = post_response.json()["id"]
    comment_response = client.post(f"/posts/{post_id}/comments", json={"text": "My comment"}, headers=auth_headers)
    comment_id = comment_response.json()["id"]

    # Login as different user
    client.post("/auth/register", json={"username": "other", "password": "otherpass123"})
    login_response = client.post("/auth/login", json={"username": "other", "password": "otherpass123"})
    other_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    # Try to delete testuser's comment
    response = client.delete(f"/comments/{comment_id}", headers=other_headers)
    assert response.status_code == 403
