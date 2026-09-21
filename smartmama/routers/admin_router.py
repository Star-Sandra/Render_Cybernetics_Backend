from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from uuid import UUID
from smartmama.schemas.auth_schema import UserSignup
from smartmama.schemas.admin_schema import AdminResponse, AdminInviteSignupRequest, AdminUpdateProfile
from smartmama.services import admin_service
from smartmama.security import require_super_admin, require_admin, TokenPayload

router = APIRouter(
    prefix="/admins",
    tags=["Administrator Core Profiles"]
)


@router.post(
    "/invite", 
    status_code=status.HTTP_201_CREATED
)
def invite_admin(
    data: UserSignup, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_super: TokenPayload = Depends(require_super_admin) #Superadmins only
):
    invite_url = admin_service.invite_new_admin(db, data, background_tasks)
    return {
        "message": "Administrator record pre-staged successfully. Verification invitation token generated.",
        "invite_url": invite_url,
    }
    
@router.post(
    "/complete-onboarding", 
    response_model=AdminResponse, 
    status_code=status.HTTP_200_OK
)
def complete_onboarding(
    data: AdminInviteSignupRequest, 
    db: Session = Depends(get_db)
):
    return admin_service.complete_admin_onboarding(db, data)
    
@router.get(
    "/current", 
    response_model=AdminResponse
)
def get_current_admin_profile(
    current_user: TokenPayload = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return admin_service.get_current_admin_profile(db, current_user.user_id)

@router.get("", response_model=list[AdminResponse])
def list_admins(skip: int = 0, limit: int = 20,
                current_super: TokenPayload = Depends(require_super_admin), db: Session = Depends(get_db)):
    return admin_service.list_admins(db, skip=skip, limit=limit)
   
@router.patch("/profile", response_model=AdminResponse)
def update_admin_profile(data: AdminUpdateProfile, db: Session = Depends(get_db),
                          current_user: TokenPayload = Depends(require_admin)):
    return admin_service.modify_admin_profile(db, current_user.user_id, data)

@router.patch("/{admin_id}/deactivate", response_model=AdminResponse)
def deactivate_admin(admin_id: UUID, db: Session = Depends(get_db),
                      current_super: TokenPayload = Depends(require_super_admin)):
    return admin_service.deactivate_admin(db, admin_id, current_super.user_id)
