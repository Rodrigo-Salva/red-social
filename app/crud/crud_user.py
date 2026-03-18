from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email, User.is_deleted == False).first()

def get_user_by_username(db: Session, username: str):
    # Asumimos que full_name se está usando como username o deberíamos tener un campo username.
    # Por ahora buscamos en full_name de manera exacta (o similar).
    return db.query(User).filter(User.full_name == username, User.is_deleted == False).first()

def get(db: Session, id: int):
    return db.query(User).filter(User.id == id, User.is_deleted == False).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()

def search_users(db: Session, query: str, skip: int = 0, limit: int = 10):
    return db.query(User).filter(
        User.is_deleted == False,
        (User.full_name.contains(query)) | (User.email.contains(query))
    ).offset(skip).limit(limit).all()

def count_search_users(db: Session, query: str) -> int:
    return db.query(User).filter(
        User.is_deleted == False,
        (User.full_name.contains(query)) | (User.email.contains(query))
    ).count()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def follow_user(db: Session, follower: User, to_follow: User):
    if to_follow.is_private:
        from app.crud.crud_follow_request import create_follow_request
        return create_follow_request(db, requester_id=follower.id, recipient_id=to_follow.id)
    
    if to_follow not in follower.following:
        follower.following.append(to_follow)
        db.commit()
    return follower

def unfollow_user(db: Session, follower: User, to_unfollow: User):
    if to_unfollow in follower.following:
        follower.following.remove(to_unfollow)
        db.commit()
    return follower

def update_user(db: Session, db_user: User, user_in: UserUpdate):
    obj_data = db_user.__dict__
    update_data = user_in.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_user, field, update_data[field])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def soft_delete_user(db: Session, db_user: User):
    db_user.is_deleted = True
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
