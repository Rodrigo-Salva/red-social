from sqlalchemy.orm import Session
from app.models.block import Block

def block_user(db: Session, blocker_id: int, blocked_id: int):
    db_block = Block(blocker_id=blocker_id, blocked_id=blocked_id)
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block

def unblock_user(db: Session, blocker_id: int, blocked_id: int):
    db_block = db.query(Block).filter(
        Block.blocker_id == blocker_id,
        Block.blocked_id == blocked_id
    ).first()
    if db_block:
        db.delete(db_block)
        db.commit()
    return db_block

def is_blocked(db: Session, blocker_id: int, blocked_id: int) -> bool:
    return db.query(Block).filter(
        Block.blocker_id == blocker_id,
        Block.blocked_id == blocked_id
    ).first() is not None

def get_blocked_users(db: Session, user_id: int):
    return db.query(Block).filter(Block.blocker_id == user_id).all()
