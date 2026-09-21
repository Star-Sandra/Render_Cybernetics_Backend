import profile
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from smartmama.schemas.ticket_schema import TicketResponse, TicketRespond, TicketCreate, TopSolverResponse
from smartmama.services import ticket_service
from smartmama.security import require_admin, get_current_user, TokenPayload

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db), _: TokenPayload = Depends(require_admin)):
    return ticket_service.list_tickets(db)

@router.post("/{ticket_id}/claim", response_model=TicketResponse)
def claim(ticket_id: UUID, db: Session = Depends(get_db), current_admin: TokenPayload = Depends(require_admin)):
    return ticket_service.claim_ticket_by_id(db, ticket_id, current_admin.user_id)

@router.patch("/{ticket_id}/respond", response_model=TicketResponse)
def respond(ticket_id: UUID, data: TicketRespond, db: Session = Depends(get_db),
            current_admin: TokenPayload = Depends(require_admin)):
    return ticket_service.respond_to_ticket_by_id(db, ticket_id, current_admin.user_id, data.status.value, data.note)

@router.post("", response_model=TicketResponse, status_code=201)
def raise_ticket(data: TicketCreate, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    return ticket_service.raise_ticket(db, data.model_dump(), current_user.user_id, current_user.role)

@router.get("/top-solvers", response_model=list[TopSolverResponse])
def get_top_solvers(db: Session = Depends(get_db), _: TokenPayload = Depends(require_admin)):
    return ticket_service.get_top_solvers(db)

