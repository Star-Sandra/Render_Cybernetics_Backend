from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from smartmama.schemas.auth_schema import UserSignup
from smartmama.schemas.supervisor_schema import (
    SupervisorResponse, 
    SupervisorInviteSignupRequest, 
    SupervisorUpdateProfile,  
)
from smartmama.services import supervisor_service
from smartmama.services.chv_verification_service import supervisor_verify_chv
from smartmama.repositories.supervisor_repository import supervisor_repository
from smartmama.security import require_admin, require_supervisor, TokenPayload


router = APIRouter(
    prefix="/supervisors",
    tags=["Supervisor Core Profiles"]
)

@router.post(
    "/invite", 
    status_code=status.HTTP_201_CREATED
)
def invite_supervisor(
    data: UserSignup, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_admin: TokenPayload = Depends(require_admin) 
):
    invite_url = supervisor_service.invite_new_supervisor(db, data, background_tasks)
    return {
        "message": "Supervisor record pre-staged successfully. Onboarding token generated.",
        "invite_url": invite_url
    }

@router.post(
    "/complete-onboarding", 
    response_model=SupervisorResponse, 
    status_code=status.HTTP_200_OK
)
def complete_onboarding(
    data: SupervisorInviteSignupRequest, 
    db: Session = Depends(get_db)
):
    return supervisor_service.complete_supervisor_onboarding(db, data)

@router.get(
    "/current", 
    response_model=SupervisorResponse
)
def get_current_supervisor_profile(
    current_user: TokenPayload = Depends(require_supervisor), # Open to Supervisors and Admins
    db: Session = Depends(get_db)
):
    return supervisor_service.get_profile_by_user_id(db, current_user.user_id)

@router.patch(
    "/profile", 
    response_model=SupervisorResponse
)
def modify_supervisor_profile(
    data: SupervisorUpdateProfile,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_supervisor)
):
    return supervisor_service.update_profile_by_user_id(db, current_user.user_id, data)
    
@router.get("", response_model=list[SupervisorResponse])
def list_supervisors(
    skip: int = 0,
    limit: int = 20,
    current_admin: TokenPayload = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return supervisor_service.get_all_supervisors(db, skip=skip, limit=limit)

@router.patch("/{supervisor_id}/deactivate", response_model=SupervisorResponse)
def deactivate_supervisor(
    supervisor_id: UUID, 
    db: Session = Depends(get_db),
    current_admin: TokenPayload = Depends(require_admin)
):
    return supervisor_service.deactivate_supervisor_by_id(db, supervisor_id, current_admin.user_id)

@router.get("/chvs")
def list_chvs(
    current_supervisor: TokenPayload = Depends(require_supervisor),
    db: Session = Depends(get_db),
):
    return supervisor_service.get_chv_oversight_list(db)

@router.get("/mothers")
def list_mothers(
    current_supervisor: TokenPayload = Depends(require_supervisor),
    db: Session = Depends(get_db),
):
    return supervisor_service.get_mother_oversight_list(db)

@router.get("/chv-verifications")
def list_pending_chvs(current_supervisor: TokenPayload = Depends(require_supervisor), db: Session = Depends(get_db)):
    return supervisor_service.get_pending_verification_list(db)

@router.patch(
    "/chv-verifications/{chv_id}", 
)
def verify_chv(
    chv_id: UUID,
    decision: str,
    rejection_notes: str | None = None,
    current_supervisor: TokenPayload = Depends(require_supervisor),
    db: Session = Depends(get_db),
):
    return supervisor_verify_chv (
        db=db,
        chv_id=chv_id,
        supervisor_id=current_supervisor.user_id,
        decision=decision,
        rejection_notes=rejection_notes
    )