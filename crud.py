from models import User as UserModel
from models import Post as PostModel
from schema import CreateUser, CreatePost, UpdatePost
from sqlalchemy.orm import Session


def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_post(db: Session, post_id: int):
    return db.query(PostModel).filter(PostModel.id == post_id).first()


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PostModel).offset(skip).limit(limit).all()


def update_post(db: Session, post_id: int, post: UpdatePost):
    db_post = get_post(db, post_id)
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}
