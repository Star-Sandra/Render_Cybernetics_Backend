from datetime import datetime, timedelta, timezone
import secrets
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks
from smartmama.models.admin_model import Admin
from smartmama.models.user_model import User
from smartmama.repositories.admin_repository import admin_repository
from smartmama.repositories.audit_log_repository import audit_log_repository
from smartmama.repositories.user_repository import user_repository
from smartmama.repositories.system_token_repository import system_token_repository
from smartmama.schemas.auth_schema import UserSignup
from smartmama.schemas.admin_schema import AdminInviteSignupRequest, AdminUpdateProfile
from smartmama.security import hash_password, hash_token, ADMIN_DASHBOARD_URL
from mailer import send_invite_email


INVITE_TOKEN_EXPIRE_HOURS = 48

def invite_new_admin(db: Session, data: UserSignup, background_tasks: BackgroundTasks) -> str:

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
        "role": "admin",
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
    invite_url = f"{ADMIN_DASHBOARD_URL}/accept-admin-invite?token={raw_token}"
    background_tasks.add_task(_try_send_admin_invite_email, email, data.first_name, invite_url)
    return invite_url

def _try_send_admin_invite_email(email: str, first_name: str, invite_url: str) -> None:
    try:
        send_invite_email(email, first_name, invite_url, "admin")
        print(f"Admin invite email sent to {email}")
    except Exception as e:
        print(f"Email failed: {e}")

def complete_admin_onboarding(db: Session, data: AdminInviteSignupRequest) -> Admin:

    db_token = system_token_repository.get_valid_token(db, data.token)
    if not db_token or db_token.token_type != "invitation":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The invitation link is invalid or has expired."
        )

    user = db.query(User).filter(User.person_id == db_token.target_person_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user identity data was not found."
        )

    user.hashed_password = hash_password(data.password)
    user.is_active = True

    system_token_repository.update_token_status(db, db_token, "ACCEPTED")

    new_admin_profile = admin_repository.create_admin_profile(
        db=db,
        user_id=user.user_id,
        is_superadmin=False 
    )

    db.commit()
    return new_admin_profile


def update_admin_profile(db: Session, user_id: UUID, data: AdminUpdateProfile) -> Admin:
    admin = admin_repository.get_admin_profile_by_user_id(db, user_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Administrative identity record not found.")

    values = data.model_dump(exclude_unset=True)

    person_updates = {}
    if "first_name" in values: person_updates["first_name"] = values.pop("first_name")
    if "last_name" in values: person_updates["last_name"] = values.pop("last_name")
    if "phone_number" in values: person_updates["phone_number"] = values.pop("phone_number")
    
    if person_updates:
        for key, val in person_updates.items():
            setattr(admin.user.person, key, val)

    user_updates = {}
    if "email" in values:
        email = str(values.pop("email")).lower()
        existing = user_repository.get_user_by_email(db, email)
        if existing and existing.user_id != admin.user_id:
            raise HTTPException(status_code=409, detail="Email already exists.")
        user_updates["email"] = email
        
    if "password" in values:
        user_updates["hashed_password"] = hash_password(values.pop("password"))

    if user_updates:
        for key, val in user_updates.items():
            setattr(admin.user, key, val)

    db.commit()
    db.refresh(admin)
    return admin

def deactivate_admin(db: Session, admin: Admin, super_admin_user_id: UUID, admin_id: UUID) -> Admin:
    admin = admin_repository.get_admin_profile(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
 
    admin.user.is_active = False
    audit_log_repository.create(db, actor_id=super_admin_user_id, event_category="action",
                                 action_type="admin_deactivated", target_id=admin.admin_id, success=True)
    db.commit()
    db.refresh(admin)
    return admin

def get_current_admin_profile(db: Session, user_id: UUID) -> Admin:
    profile = admin_repository.get_admin_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Administrative identity record not found.")
    return profile

def list_admins(db: Session, skip: int = 0, limit: int = 20) -> list[Admin]:
    return admin_repository.list_admins(db, skip=skip, limit=limit)
