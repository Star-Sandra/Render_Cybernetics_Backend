from fastapi import HTTPException, status
from smartmama.security import hash_token, secrets, CONSENT_PAGE_URL
from smartmama.models import Mother
from database import Session
from datetime import datetime, timedelta, timezone
from smartmama.repositories import system_token_repository, mother_repository
from smartmama.services import sms_service 

def generate_consent_link(db: Session, mother: Mother) -> str:
    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=72)
    system_token_repository.create_token(
        db=db, 
        token_hash=hash_token(raw_token), 
        token_type="consent",
        target_person_id=mother.mother_id, 
        expires_at=expires_at,
    )
    return f"{CONSENT_PAGE_URL}/consent?token={raw_token}"

def send_consent_link(db: Session, mother_id) -> str:
    mother = mother_repository.get_mother_by_id(db, mother_id)
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    url = generate_consent_link(db, mother)
    message = (
        f"Dear {mother.person.first_name}, Please confirm you consent to SmartMama's terms and conditions "
        f"by visiting: {url}"
    )
    sms_service.dispatch_system_sms_sync(mother.phone_number, message)
    return url

def accept_consent(db: Session, raw_token: str) -> Mother:
    token = system_token_repository.get_valid_token(db, raw_token)
    if not token or token.token_type != "consent":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This consent link is invalid or has expired."
        )

    mother = mother_repository.get_mother_by_id(db, token.target_person_id)
    if not mother:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Associated mother record was not found."
        )

    mother.consent_given = True
    system_token_repository.update_token_status(db, token, "ACCEPTED")
    db.commit()
    db.refresh(mother)
    return mother