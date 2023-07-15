import os
import crud
import security

from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, PlainTextResponse
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from schema import CreateUser, UserAuth, CreatePost, UpdatePost
from models import User as UserModel
from models import Post as PostModel
from models import Like as LikeModel
from models import get_db, SessionLocal, DBSession

from dotenv import load_dotenv
from typing import Optional

load_dotenv('.env')

app = FastAPI()
bearer_scheme = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.post("/register")
async def register(user: CreateUser, db: Session = Depends(get_db)):
    password_hash = security.get_password_hash(user.password)
    db_user = UserModel(name=user.name, surname=user.surname, email=user.email, password=password_hash)
    if crud.get_user_by_email(db, db_user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    db.add(db_user)
    db.commit()


@app.post("/auth")
async def login(user_in: UserAuth, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter((UserModel.name == user_in.name) | (UserModel.email == user_in.email)).first()
    if user is None or not security.verify_password(user_in.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid name or password")
    access_token = security.create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/posts/")
async def create_post(post: CreatePost, db: Session = Depends(get_db),
                      current_user: UserModel = Depends(security.get_current_user)):
    db_post = PostModel(title=post.title, content=post.content, user_id=post.user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: UpdatePost, db: Session = Depends(get_db),
                      current_user: UserModel = Depends(security.get_current_user)):
    db_post = crud.get_post(db=db, post_id=post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return crud.update_post(db=db, post_id=post_id, post=post)


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db),
                      current_user: UserModel = Depends(security.get_current_user)):
    db_post = crud.get_post(db=db, post_id=post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return crud.delete_post(db=db, post_id=post_id)


@app.get("/posts/")
async def read_posts(db: Session = Depends(get_db), current_user: UserModel = Depends(security.get_current_user)):
    posts = db.query(PostModel).all()
    return posts


@app.post("/posts/{post_id}/like")
async def like_post(post_id: int, db: Session = Depends(get_db),
                    current_user: UserModel = Depends(security.get_current_user)):
    post = db.query(PostModel).get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot like your own post")
    if db.query(LikeModel).filter_by(post_id=post_id, user_id=current_user.id).first():
        raise HTTPException(status_code=400, detail="You have already liked this post")
    like = LikeModel(post_id=post_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    return {"message": "Post liked successfully"}


@app.post("/posts/{post_id}/dislike")
async def dislike_post(post_id: int, db: Session = Depends(get_db),
                       current_user: UserModel = Depends(security.get_current_user)):
    try:
        post = db.query(PostModel).get(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id == current_user.id:
            raise HTTPException(status_code=400, detail="You cannot dislike your own post")
        like = db.query(LikeModel).filter_by(post_id=post_id, user_id=current_user.id).first()
        if not like:
            raise HTTPException(status_code=400, detail="You have not liked this post")
        db.delete(like)
        db.commit()
        return {"message": "Post disliked successfully"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Internal server error")
