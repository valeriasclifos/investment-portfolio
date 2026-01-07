from services.database import SessionLocal
from models.user import User
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    db = SessionLocal()
    if db.query(User).filter_by(username=username).first():
        return False, "Utilizatorul există deja."

    user = User(username=username, password_hash=hash_password(password), balance=0.0)
    db.add(user)
    db.commit()
    return True, "Cont creat cu succes."

def login(username, password):
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()

    if not user:
        return False, "Utilizator inexistent."

    if user.password_hash != hash_password(password):
        return False, "Parolă greșită."

    return True, user
