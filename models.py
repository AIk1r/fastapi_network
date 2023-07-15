import os

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.sql import func

from dotenv import load_dotenv

Base = declarative_base()

load_dotenv()

POSTGRES_URL = os.getenv('DATABASE_URL')

engine = create_engine(
    POSTGRES_URL, echo=True
)
DBSession = Session(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user
        else:
            return None
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    password = Column(String)
    email = Column(String, unique=True, index=True)

    posts = relationship('Post', back_populates='user')
    likes = relationship('Like', back_populates='user')


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='posts')
    likes = relationship('Like', back_populates='post')


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")
