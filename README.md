# Blog API

A RESTful blog API built with FastAPI. Users can register, write posts, and comment on each other's posts.

## Features

- JWT authentication (register, login, token-based access)
- CRUD operations for posts and comments
- Role-based access control (user vs admin)
- Pagination on post listing
- Ownership checks — users can only modify their own content
- Admins can delete any post or comment
- Automated tests with pytest

## Tech Stack

- **FastAPI** — web framework
- **SQLModel** — ORM (SQLAlchemy + Pydantic)
- **SQLite** — database
- **PyJWT** — JSON Web Tokens
- **pwdlib** — password hashing (Argon2)
- **pytest** — testing

## Project Structure

```
Blog-app/
├── app/
│   ├── main.py              # app entry point
│   ├── auth.py              # JWT + password hashing
│   ├── database.py          # engine + session
│   ├── models/
│   │   ├── user_model.py    # User + schemas
│   │   ├── post_model.py    # Post + schemas
│   │   └── comment_model.py # Comment + schemas
│   └── routes/
│       ├── auth.py          # register, login
│       ├── posts.py         # post CRUD + pagination
│       └── comments.py      # comment create, list, delete
├── tests/
│   ├── conftest.py          # test fixtures
│   ├── test_auth.py
│   ├── test_posts.py
│   └── test_comments.py
├── requirements.txt
└── .env.example
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set a real SECRET_KEY
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## API Endpoints

### Auth
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login, get JWT token | No |

### Posts
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/posts?page=1&limit=10` | List posts (paginated) | No |
| GET | `/posts/{id}` | Get a single post | No |
| POST | `/posts` | Create a post | Yes |
| PUT | `/posts/{id}` | Update your post | Yes |
| DELETE | `/posts/{id}` | Delete post (owner or admin) | Yes |

### Comments
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/posts/{id}/comments` | List comments on a post | No |
| POST | `/posts/{id}/comments` | Add a comment | Yes |
| DELETE | `/comments/{id}` | Delete comment (owner or admin) | Yes |

## Run Tests

```bash
pytest tests/ -v
```
