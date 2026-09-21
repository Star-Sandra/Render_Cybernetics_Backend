from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from smartmama.services import consent_service
from smartmama.security import require_chv

router = APIRouter(prefix="/consent", tags=["Consent"])


@router.post("/{mother_id}/send", status_code=status.HTTP_200_OK)
def send_consent_link(
    mother_id: UUID,
    db: Session = Depends(get_db),
    current_chv=Depends(require_chv),
):
    url = consent_service.send_consent_link(db, mother_id)
    return {"consent_url": url}
        
@router.post("/{token}/accept", status_code=status.HTTP_200_OK)
def accept_consent(token: str, db: Session = Depends(get_db)):
    consent_service.accept_consent(db, token)
    return {"message": "Consent recorded successfully."}