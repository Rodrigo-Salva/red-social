from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.story import Story
from app.schemas.story import StoryCreate
from app.models.user import User

def create_story(db: Session, story: StoryCreate, owner_id: int):
    # Por defecto expira en 24 horas
    expires_at = datetime.now() + timedelta(hours=24)
    db_story = Story(
        **story.dict(),
        owner_id=owner_id,
        expires_at=expires_at
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

def get_active_stories_for_user_feed(db: Session, user: User):
    # Historias de gente que sigue + las suyas propias
    followed_ids = [u.id for u in user.following]
    followed_ids.append(user.id)
    
    now = datetime.now()
    return db.query(Story).filter(
        Story.owner_id.in_(followed_ids),
        Story.is_deleted == False,
        Story.expires_at > now
    ).order_by(Story.created_at.desc()).all()

def get_user_stories(db: Session, user_id: int):
    now = datetime.now()
    return db.query(Story).filter(
        Story.owner_id == user_id,
        Story.is_deleted == False,
        Story.expires_at > now
    ).order_by(Story.created_at.desc()).all()

def delete_story(db: Session, story_id: int):
    db_story = db.query(Story).filter(Story.id == story_id).first()
    if db_story:
        db_story.is_deleted = True
        db.add(db_story)
        db.commit()
    return db_story
