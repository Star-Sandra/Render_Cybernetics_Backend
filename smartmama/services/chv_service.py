from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from smartmama.models.chv import CHV
from smartmama.repositories.chv_repository import chv_repository
from smartmama.repositories.user_repository import user_repository
from smartmama.repositories.audit_log_repository import audit_log_repository
from smartmama.repositories.supervisor_repository import supervisor_repository
from smartmama.schemas.chv_schema import CHVUpdateProfile
from smartmama.schemas.auth_schema import UserSignup, UserLogin
from smartmama.security import (
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)

def signup(db: Session, data: UserSignup) -> CHV:
    email = str(data.email).lower()
    
    existing_user = user_repository.get_user_by_email(db, email)
    if existing_user:
        raise ValueError("Email already registered")
    
    person_data = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "phone_number": data.phone_number,
    }
    
    user_data = {
        "email": email,
        "hashed_password": hash_password(data.password),
        "role": "chv",
        "is_active": True
    }
    
    new_user = user_repository.create_user_and_person(db, person_data, user_data)
    return chv_repository.create_chv_profile(db, new_user.user_id)

def login(db: Session, data: UserLogin) -> str:
    user = user_repository.get_user_by_email(db, str(data.email).lower())
    if not user or not verify_password(data.password, user.hashed_password):
        raise ValueError("Invalid email or password")
    if not user.is_active:
        raise ValueError("Account is not active")

    chv = chv_repository.get_chv_profile_by_user_id(db, user.user_id)
    if not chv:
        raise ValueError("CHV profile not found")

    return create_access_token(subject=str(user.user_id), role="chv")

def update_profile(db: Session, chv: CHV, data: CHVUpdateProfile) -> CHV:
    values = data.model_dump(exclude_unset=True)
    
    person_updates = {}
    if "first_name" in values: person_updates["first_name"] = values.pop("first_name")
    if "last_name" in values: person_updates["last_name"]=values.pop("last_name")
    if "phone_number" in values: person_updates["phone_number"] = values.pop("phone_number")
    if "profile_photo_url" in values: person_updates["profile_photo_url"] = values.pop("profile_photo_url")
    if person_updates:
        for key, val in person_updates.items():
            setattr(chv.user.person, key, val)
    
    user_updates = {}    
    if "email" in values:
        email = str(values["email"]).lower()
        existing = user_repository.get_user_by_email(db, email)
        if existing and existing.user_id != chv.user_id:
            raise ValueError("Email already exists")
        user_updates["email"] = email
        
    if "password" in values:
        user_updates["hashed_password"] = hash_password(values.pop("password"))
    
    if user_updates:
        for key, val in user_updates.items():
            setattr(chv.user, key, val)
    if values:
        chv_repository.update_chv_profile(db, chv, values)
    db.commit()
    db.refresh(chv)
    return chv



def delete_own_profile(db: Session, user_id: UUID) -> CHV:
    chv = chv_repository.get_chv_profile_by_user_id(db, user_id)
    if not chv:
        raise HTTPException(status_code=404, detail="CHV profile record not found")
    return chv_repository.delete_chv_profile(db, chv)

def deactivate_chv(db: Session, chv: CHV, supervisor_user_id: UUID, reason: str) -> CHV:
    return chv_repository.deactivate_chv(db, chv, supervisor_user_id, reason)


def approve_cert(db: Session, chv_id: UUID, supervisor_user_id: UUID) -> CHV:
    chv = get_chv(db, chv_id)
    sup = supervisor_repository.get_supervisor_profile_by_user_id(db, supervisor_user_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supervisor profile not found")
    return approve_cert(db, chv, sup.supervisor_id, supervisor_user_id)


def reject_cert(db: Session, chv_id: UUID, supervisor_user_id: UUID, notes: str) -> CHV:
    chv = get_chv(db, chv_id)
    sup = supervisor_repository.get_supervisor_profile_by_user_id(db, supervisor_user_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supervisor profile not found")
    return reject_cert(db, chv, sup.supervisor_id, supervisor_user_id, notes)


def get_chv(db: Session, chv_id: UUID) -> CHV:
    chv = chv_repository.get_chv_profile(db, chv_id)
    if not chv:
        raise HTTPException(status_code=404, detail="CHV not found")
    return 