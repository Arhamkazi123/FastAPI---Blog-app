def test_register_user(client):
    """New user should get 201 with id and username back"""
    response = client.post("/auth/register", json={
        "username": "john",
        "password": "secret123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "john"
    assert "id" in data
    # password should NOT be in the response
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_user(client):
    """Registering same username twice should fail"""
    client.post("/auth/register", json={"username": "john", "password": "secret123"})
    response = client.post("/auth/register", json={"username": "john", "password": "secret123"})
    assert response.status_code == 400
    assert response.json()["detail"] == "username already exists"


def test_register_short_password(client):
    """Password under 6 chars should fail validation"""
    response = client.post("/auth/register", json={"username": "john", "password": "abc"})
    assert response.status_code == 422  # validation error


def test_login_success(client):
    """Login with correct credentials should return a token"""
    client.post("/auth/register", json={"username": "john", "password": "secret123"})
    response = client.post("/auth/login", json={"username": "john", "password": "secret123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Login with wrong password should return 401"""
    client.post("/auth/register", json={"username": "john", "password": "secret123"})
    response = client.post("/auth/login", json={"username": "john", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_nonexistent_user(client):
    """Login with a username that doesn't exist should return 401"""
    response = client.post("/auth/login", json={"username": "ghost", "password": "secret123"})
    assert response.status_code == 401
