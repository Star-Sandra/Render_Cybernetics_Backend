from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, model_validator
from datetime import datetime
from typing import Optional

class SupervisorInviteSignupRequest(BaseModel):    
    token: str
    password: str

class SupervisorResponse(BaseModel):    
    model_config = ConfigDict(from_attributes=True)

    supervisor_id: UUID
    user_id: UUID
    first_name: str            
    last_name: str             
    email: EmailStr            
    phone_number: Optional[str] = None 
    mfa_enabled: bool = False
    created_at: datetime
    
    @model_validator(mode="before")
    @classmethod
    def flatten_related_fields(cls, obj):
        if isinstance(obj, dict):
            return obj
        user = getattr(obj, "user", None)
        person = getattr(user, "person", None) if user else None
        return {
            "supervisor_id": obj.supervisor_id,
            "user_id": obj.user_id,
            "first_name": person.first_name if person else "",
            "last_name": person.last_name if person else "",
            "phone_number": person.phone_number if person else None,
            "email": user.email if user else None,
            "mfa_enabled": getattr(user, "mfa_enabled", False) if user else False,
            "created_at": user.created_at if user else None,
        } 

class SupervisorUpdateProfile(BaseModel):
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    old_password: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    
class VerifyCHVActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chv_id: UUID
    certificate_status: str
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    rejection_notes: Optional[str] = None