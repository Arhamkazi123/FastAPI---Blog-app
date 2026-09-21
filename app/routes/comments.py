from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from app.database import get_session
from app.models import Comment, CommentRead, CommentCreate, Post, User
from app.auth import get_current_user


router = APIRouter(tags=["comments"])


@router.get("/posts/{post_id}/comments", response_model=list[CommentRead])
def get_comments(
    post_id: int,
    session: Session = Depends(get_session),
):
    comments = session.exec(select(Comment).where(Comment.post_id == post_id)).all()
    return comments


@router.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment: CommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    db_comment = Comment(
        text=comment.text,
        user_id=current_user.id,
        post_id=post_id,
    )

    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    comment = session.get(Comment, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    session.delete(comment)
    session.commit()
