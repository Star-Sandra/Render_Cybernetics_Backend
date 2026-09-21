from datetime import datetime, timedelta, timezone
from uuid import UUID
import secrets
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks
from smartmama.models.supervisor_model import Supervisor
from smartmama.models.user_model import User
from smartmama.repositories.supervisor_repository import supervisor_repository
from smartmama.repositories.user_repository import user_repository
from smartmama.repositories.system_token_repository import system_token_repository
from smartmama.repositories.audit_log_repository import audit_log_repository
from smartmama.schemas.auth_schema import UserSignup
from smartmama.schemas.supervisor_schema import SupervisorInviteSignupRequest, SupervisorUpdateProfile
from smartmama.repositories.chv_repository import chv_repository
from smartmama.repositories.mother_repository import mother_repository
from smartmama.security import hash_password, hash_token, verify_password, ADMIN_DASHBOARD_URL
from mailer import send_invite_email
import logging

logger = logging.getLogger(__name__)

INVITE_TOKEN_EXPIRE_HOURS = 48

def invite_new_supervisor(db: Session, data: UserSignup, background_tasks: BackgroundTasks) -> str:    
    email = str(data.email).lower()
    existing_user = user_repository.get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered."
        )

    person_data = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "phone_number": data.phone_number,
        "location_name": None
    }
    
    user_data = {
        "email": email,
        "hashed_password": hash_password(secrets.token_urlsafe(16)),  
        "role": "supervisor",
        "is_active": False 
    }
    new_user = user_repository.create_user_and_person(db, person_data, user_data)
    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=INVITE_TOKEN_EXPIRE_HOURS)
    system_token_repository.create_token(
        db=db,
        token_hash=hash_token(raw_token),
        token_type="invitation",
        target_person_id=new_user.person_id,
        expires_at=expires_at
    )
    db.commit()
    invite_url = f"{ADMIN_DASHBOARD_URL}/accept-supervisor-invite?token={raw_token}"
    background_tasks.add_task(_try_send_invite_email, email, data.first_name, invite_url, "supervisor")
      
    return invite_url

def _try_send_invite_email(email: str, first_name: str, invite_url: str, role: str) -> None:
    try:
        send_invite_email(email, first_name, invite_url, role)
    except Exception as email_error:
        logger.error(f"Background automation invitation email failed to deliver: {email_error}")

def complete_supervisor_onboarding(db: Session, data: SupervisorInviteSignupRequest) -> Supervisor:   
    db_token = system_token_repository.get_valid_token(db, data.token)
    if not db_token or db_token.token_type != "invitation":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The invitation link is invalid or has expired."
        )
    user = user_repository.get_user_by_person_id(db, db_token.target_person_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user identity data was not found."
        )

    user.hashed_password = hash_password(data.password)
    user.is_active = True
    system_token_repository.update_token_status(db, db_token, "ACCEPTED")
    new_supervisor_profile = supervisor_repository.create_supervisor_profile(
        db=db,
        user_id=user.user_id
    )
    return new_supervisor_profile

def get_all_supervisors(db: Session, skip: int = 0, limit: int = 20) -> list[Supervisor]:
    return supervisor_repository.list_supervisors(db, skip=skip, limit=limit)

def get_profile_by_user_id(db: Session, user_id: UUID) -> Supervisor:
    supervisor = supervisor_repository.get_supervisor_profile_by_user_id(db, user_id)
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor profile not found.")
    return supervisor

def update_supervisor_profile(db: Session, supervisor: Supervisor, data: SupervisorUpdateProfile) -> Supervisor:
    values = data.model_dump(exclude_unset=True)

    person_updates = {}
    if "first_name" in values: person_updates["first_name"] = values.pop("first_name")
    if "last_name" in values: person_updates["last_name"] = values.pop("last_name")
    if "phone_number" in values: person_updates["phone_number"] = values.pop("phone_number")
    
    if person_updates:
        for key, val in person_updates.items():
            setattr(supervisor.user.person, key, val)

    user_updates = {}
    if "email" in values:
        email = str(values.pop("email")).lower()
        existing = user_repository.get_user_by_email(db, email)
        if existing and existing.user_id != supervisor.user_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")
        user_updates["email"] = email       
    old_password = values.pop("old_password", None)
    if "password" in values:
        if not old_password or not verify_password(old_password, supervisor.user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect.")
        user_updates["hashed_password"] = hash_password(values.pop("password"))

    if user_updates:
        for key, val in user_updates.items():
            setattr(supervisor.user, key, val)
    return supervisor_repository.save(db, supervisor)

def update_profile_by_user_id(db: Session, user_id: UUID, data: SupervisorUpdateProfile) -> Supervisor:
    supervisor = get_profile_by_user_id(db, user_id)
    return update_supervisor_profile(db, supervisor, data)

def deactivate_supervisor(db: Session, supervisor: Supervisor, admin_user_id: UUID) -> Supervisor:
    supervisor.user.is_active = False
    audit_log_repository.create(
        db, 
        actor_id=admin_user_id, 
        event_category="action",
        action_type="supervisor_deactivated", 
        target_id=supervisor.supervisor_id,
        success=True
    )
    return supervisor_repository.save(db, supervisor)

def deactivate_supervisor_by_id(db: Session, supervisor_id: UUID, admin_user_id: UUID) -> Supervisor:
    supervisor = supervisor_repository.get_supervisor_profile(db, supervisor_id)
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor not found.")
    return deactivate_supervisor(db, supervisor, admin_user_id)

def get_chv_oversight_list(db: Session):
    return chv_repository.list_chvs_with_details(db)

def get_mother_oversight_list(db: Session):
    return mother_repository.list_mothers_with_details(db)

def get_pending_verification_list(db: Session):
    return chv_repository.list_pending_verifications(db)
