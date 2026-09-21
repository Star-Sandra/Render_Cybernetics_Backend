from sqlalchemy.orm import Session
from smartmama.repositories.audit_log_repository import audit_log_repository

def get_system_audit_logs(db: Session, skip: int, limit: int):
    return audit_log_repository.list_all(db, skip=skip, limit=limit)
