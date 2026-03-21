from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.poll import Poll, PollOption, PollVote
from app.schemas.poll import PollCreate, PollVoteCreate

def create_poll(db: Session, post_id: int, poll_in: PollCreate):
    db_poll = Poll(
        question=poll_in.question,
        post_id=post_id,
        expires_at=poll_in.expires_at
    )
    db.add(db_poll)
    db.commit()
    db.refresh(db_poll)
    
    for option_text in poll_in.options:
        db_option = PollOption(poll_id=db_poll.id, text=option_text)
        db.add(db_option)
    
    db.commit()
    db.refresh(db_poll)
    return db_poll

def vote_in_poll(db: Session, poll_id: int, user_id: int, option_id: int):
    # Verificar si ya votó
    existing_vote = db.query(PollVote).filter(
        PollVote.poll_id == poll_id,
        PollVote.user_id == user_id
    ).first()
    
    if existing_vote:
        # Podríamos permitir cambiar el voto, pero por ahora lanzamos error o ignoramos
        # Vamos a permitir cambiarlo si el user elige otra opción
        if existing_vote.option_id == option_id:
            return existing_vote
        existing_vote.option_id = option_id
    else:
        db_vote = PollVote(poll_id=poll_id, option_id=option_id, user_id=user_id)
        db.add(db_vote)
    
    db.commit()
    return True

def get_poll_results(db: Session, poll_id: int):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        return None
    
    return poll

def delete_poll(db: Session, poll_id: int):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if poll:
        db.delete(poll)
        db.commit()
    return poll
