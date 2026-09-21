from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from app.database import get_session
from app.models import Post, PostRead, PostCreate, User
from app.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostRead])
def get_posts(
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    offset = (page - 1) * limit
    posts = session.exec(select(Post).offset(offset).limit(limit)).all()
    return posts


@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    post: PostCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_post = Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
    )

    session.add(db_post)
    session.commit()
    session.refresh(db_post)

    return db_post


@router.get("/{post_id}", response_model=PostRead)
def get_single_post(
    post_id: int,
    session: Session = Depends(get_session),
):
    post = session.get(Post, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    post_data: PostCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    post = session.get(Post, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts",
        )

    post.title = post_data.title
    post.content = post_data.content

    session.add(post)
    session.commit()
    session.refresh(post)

    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    post = session.get(Post, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Owner OR admin can delete
    if post.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts",
        )

    session.delete(post)
    session.commit()
