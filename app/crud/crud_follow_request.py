from sqlalchemy.orm import Session
from app.models.follow_request import FollowRequest, FollowRequestStatus

def create_follow_request(db: Session, requester_id: int, recipient_id: int):
    db_obj = FollowRequest(requester_id=requester_id, recipient_id=recipient_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_follow_request(db: Session, request_id: int):
    return db.query(FollowRequest).filter(FollowRequest.id == request_id).first()

def get_pending_requests(db: Session, user_id: int):
    return db.query(FollowRequest).filter(
        FollowRequest.recipient_id == user_id,
        FollowRequest.status == FollowRequestStatus.PENDING
    ).all()

def update_follow_request_status(db: Session, db_obj: FollowRequest, status: FollowRequestStatus):
    db_obj.status = status
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
