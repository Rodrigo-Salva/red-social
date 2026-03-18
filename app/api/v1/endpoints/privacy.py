from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.patch("/me", response_model=schemas.user.User)
def update_privacy(
    *,
    db: Session = Depends(deps.get_db),
    is_private: bool,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Cambiar el estado de privacidad de la cuenta.
    """
    current_user.is_private = is_private
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/requests", response_model=List[schemas.follow_request.FollowRequest])
def get_requests(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Ver solicitudes de seguimiento pendientes.
    """
    return crud.crud_follow_request.get_pending_requests(db, user_id=current_user.id)

@router.post("/requests/{request_id}/accept", response_model=schemas.follow_request.FollowRequest)
def accept_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Aceptar una solicitud de seguimiento.
    """
    request = crud.crud_follow_request.get_follow_request(db, request_id=request_id)
    if not request or request.recipient_id != current_user.id:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # Añadir a seguidores
    requester = crud.get(db, id=request.requester_id)
    crud.follow_user(db, follower=requester, to_follow=current_user)
    
    return crud.crud_follow_request.update_follow_request_status(
        db, db_obj=request, status=schemas.follow_request.FollowRequestStatus.ACCEPTED
    )

@router.post("/requests/{request_id}/reject", response_model=schemas.follow_request.FollowRequest)
def reject_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Rechazar una solicitud de seguimiento.
    """
    request = crud.crud_follow_request.get_follow_request(db, request_id=request_id)
    if not request or request.recipient_id != current_user.id:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    return crud.crud_follow_request.update_follow_request_status(
        db, db_obj=request, status=schemas.follow_request.FollowRequestStatus.REJECTED
    )
