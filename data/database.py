from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy import create_engine, and_
from datetime import datetime, timedelta

MENU_MAIN = "main"
MENU_CREATE = "create"
MENU_VIEW = "view"
MENU_EDIT = "edit"

Base = declarative_base()

DATABASE_URL = "sqlite:///./bot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)  # Telegram ID
    user_fullname = Column(String, nullable=False)
    notes = relationship("Note", back_populates="user")


class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    data_start = Column(DateTime, default=datetime.utcnow)
    data_end = Column(DateTime, nullable=False)
    note_title = Column(String, nullable=False)
    note_text = Column(String, nullable=True)  # Может быть пустым
    is_completed = Column(Boolean, default=False)  # Сделан ли дедлайн

    user = relationship("User", back_populates="notes")


Base.metadata.create_all(bind=engine)


# Класс для работы с БД
class Database:
    def __init__(self):
        self.SessionLocal = SessionLocal

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Пользователи
    def create_user(self, user_id: int, user_fullname: str):
        db = self.SessionLocal()
        db_user = User(user_id=user_id, user_fullname=user_fullname)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user(self, user_id: int):
        db = self.SessionLocal()
        return db.query(User).filter(User.user_id == user_id).first()

    def get_user_menu_state(self, user_id: int) -> str:
        db = self.SessionLocal()
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            return user.menu_state
        return MENU_MAIN

    def set_user_menu_state(self, user_id: int, state: str):
        db = self.SessionLocal()
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.menu_state = state
            db.commit()
            db.refresh(user)
        return user

    # Заметки
    def create_note(self, user_id: int, data_start: datetime, data_end: datetime, note_title: str, note_text: str):
        db = self.SessionLocal()
        db_note = Note(
            user_id=user_id,
            data_start=data_start,
            data_end=data_end,
            note_title=note_title,
            note_text=note_text
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

    def get_note(self, note_id: int):
        db = self.SessionLocal()
        return db.query(Note).filter(Note.note_id == note_id).first()

    def get_notes_by_user_id(self, user_id: int):
        db = self.SessionLocal()
        return db.query(Note).filter(Note.user_id == user_id).all()

    def get_note_ids_by_user_id(self, user_id: int):
        db = self.SessionLocal()
        notes = db.query(Note.note_id).filter(Note.user_id == user_id).all()
        return [note[0] for note in notes]

    def update_note_deadline(self, note_id: int, new_data_end: datetime):
        db = self.SessionLocal()
        note = db.query(Note).filter(Note.note_id == note_id).first()
        if note:
            note.data_end = new_data_end
            db.commit()
            db.refresh(note)
            return note
        return None

    def update_note_title(self, note_id: int, new_title: str):
        db = self.SessionLocal()
        note = db.query(Note).filter(Note.note_id == note_id).first()
        if note:
            note.note_title = new_title
            db.commit()
            db.refresh(note)
            return note
        return None

    def update_note_text(self, note_id: int, new_text: str):
        db = self.SessionLocal()
        note = db.query(Note).filter(Note.note_id == note_id).first()
        if note:
            note.note_text = new_text
            db.commit()
            db.refresh(note)
            return note
        return None

    def delete_note(self, note_id: int):
        db = self.SessionLocal()
        note = db.query(Note).filter(Note.note_id == note_id).first()
        if note:
            db.delete(note)
            db.commit()
            return True
        return False

    def mark_note_as_completed(self, note_id: int):
        db = self.SessionLocal()
        note = db.query(Note).filter(Note.note_id == note_id).first()
        if note:
            note.is_completed = True
            db.commit()
            db.refresh(note)

    def mark_note_as_uncompleted(self, note_id: int):
        db = self.SessionLocal()
        note = db.query(Note).filter(Note.note_id == note_id).first()
        if note:
            note.is_completed = False
            db.commit()
            db.refresh(note)
