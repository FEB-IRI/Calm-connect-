from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import Session, DeclarativeBase


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_login = Column(DateTime)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    session_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)

class Therapist(Base):
    __tablename__ = "therapists"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    specialty = Column(String, nullable=False)
    bio = Column(String)
    pic = Column(String)

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, nullable=False)
    recipient_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

class GroupChat(Base):
    __tablename__ = "group_chats"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

class WellnessTest(Base):
    __tablename__ = "wellness_tests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

engine = create_engine("sqlite:///project.db")
Base.metadata.create_all(engine)
db = Session(engine)
