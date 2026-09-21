from uuid import UUID
from sqlalchemy.orm import Session
from smartmama.models.chv import CHV
from smartmama.models.token_model import RevokedToken
from smartmama.models.user_model import User

class CHVRepository:
    def __init__(self):
        self.model = CHV

    def get_chv_profile(self, db: Session, chv_id: UUID) -> CHV | None:
        return (
            db.query(self.model)
            .filter(self.model.chv_id == chv_id)
            .first()
        )
    
    def get_chv_profile_by_user_id(self, db: Session, user_id: UUID) -> CHV | None:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .first()
        )

    def create_chv_profile(self, db: Session, user_id: UUID) -> CHV:
        db_chv = self.model(
            user_id=user_id,
            certificate_status="Pending"
        )
        db.add(db_chv)
        db.commit()
        db.refresh(db_chv)
        return db_chv

    def update_chv_profile(self, db: Session, chv: CHV, data: dict) -> CHV:
        for key, value in data.items():
            if hasattr(chv, key):
                setattr(chv, key, value)
        db.commit()
        db.refresh(chv)
        return chv

    def delete_chv_profile(self, db: Session, chv: CHV) -> CHV:
        if chv.user:
            chv.is_active = False
            db.commit()
            db.refresh(chv)
        return chv
    
    def list_chvs_with_details(self, db: Session) -> list[CHV]:
        return (
            db.query(self.model)
            .join(self.model.user)
            .join(User.person)
            .all()
        )
    def list_pending_verifications(self, db: Session) -> list[CHV]:
        return (
            db.query(self.model)
            .join(self.model.user)
            .join(User.person)
            .filter(self.model.certificate_status == "Pending")
            .all()
        )    

chv_repository = CHVRepository()
