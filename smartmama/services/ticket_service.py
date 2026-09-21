from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from smartmama.models.ticket_model import Ticket
from smartmama.repositories.ticket_repository import ticket_repository
from smartmama.repositories.audit_log_repository import audit_log_repository
from smartmama.repositories.admin_repository import admin_repository


def claim_ticket(db: Session, ticket: Ticket, admin_user_id: UUID, admin_id: UUID) -> Ticket:
    ticket.assigned_to = admin_id
    ticket.status = "Pending"
    audit_log_repository.create(
        db, actor_id=admin_user_id, event_category="action",
        action_type="ticket_claimed", target_id=ticket.ticket_id, success=True,
    )
    return ticket_repository.save(db, ticket)

def respond_to_ticket(db: Session, ticket: Ticket, admin_user_id: UUID, status: str, note: str | None) -> Ticket:
    ticket.status = status
    ticket.response_note = note
    if status == "Solved":
        ticket.resolved_at = datetime.now(timezone.utc)
    audit_log_repository.create(
        db, actor_id=admin_user_id, event_category="action",
        action_type="ticket_responded", target_id=ticket.ticket_id,
        success=True, details=note,
    )
    return ticket_repository.save(db, ticket)

def raise_ticket(db: Session, data: dict, raiser_user_id: UUID, raiser_role: str) -> Ticket:
    data["raised_by_id"] = raiser_user_id
    data["raised_by_type"] = raiser_role
    ticket = ticket_repository.create(db, data)
    audit_log_repository.create(
        db, actor_id=raiser_user_id, event_category="action",
        action_type="ticket_raised", target_id=ticket.ticket_id, success=True,
    )
    return ticket

def list_tickets(db: Session):
    return ticket_repository.list_all(db)
def get_top_solvers(db: Session) -> list[dict]:
    rows = ticket_repository.top_solvers(db)
    return [
        {"name": f"{first_name} {last_name}".strip(), "tickets": solved_count}
        for first_name, last_name, solved_count in rows
    ]

def claim_ticket_by_id(db: Session, ticket_id: UUID, admin_user_id: UUID) -> Ticket:
    ticket = ticket_repository.get(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    admin_profile = admin_repository.get_admin_profile_by_user_id(db, admin_user_id)
    if not admin_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin profile not found")
    return claim_ticket(db, ticket, admin_user_id, admin_profile.admin_id)

def respond_to_ticket_by_id(db: Session, ticket_id: UUID, admin_user_id: UUID, status: str, note: str | None) -> Ticket:
    ticket = ticket_repository.get(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return respond_to_ticket(db, ticket, admin_user_id, status, note)
