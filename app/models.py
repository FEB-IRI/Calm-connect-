from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import Session, DeclarativeBase
from datetime import datetime

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
    group_name = Column(String, nullable=False)
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

def setup_group_chat(group_name, admin_fullname, admin_username, admin_email, admin_password, welcome_message="Welcome to the group!"):
    """
    Sets up a group chat. If the group doesn't exist yet, it creates one with an admin.
    It also sends a default welcome message to the group and creates the admin account.
    """
    # Check if the group chat already exists
    group_chat = db.query(GroupChat).filter_by(group_name=group_name).first()
    if group_chat is None:
        # Create an admin account
        admin_user = User(fullname=admin_fullname, username=admin_username, email=admin_email, password=admin_password, created_at=datetime.now())
        db.add(admin_user)
        db.commit()
        
        # Create the group chat with the admin as the sender
        group_chat = GroupChat(group_name=group_name, sender_id=admin_user.id, message=welcome_message, created_at=datetime.now())
        db.add(group_chat)
        db.commit()


setup_group_chat('Mental Health', "Administrator", 'Administrator', 'admin@gmail.com', '1qaz@WSX')