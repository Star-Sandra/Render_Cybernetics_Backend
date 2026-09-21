from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, model_validator
from datetime import datetime
from typing import Optional

class AdminInviteSignupRequest(BaseModel):
    
    token: str
    password: str

class AdminResponse(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)

    admin_id: UUID
    user_id: UUID
    first_name: str            
    last_name: str             
    email: EmailStr            
    phone_number: Optional[str] = None 
    is_superadmin: bool   
    mfa_enabled: bool = False     
    created_at: datetime
    
    @model_validator(mode="before")
    @classmethod
    def flatten_related_fields(cls, obj):
        """Turns a raw Admin ORM object into the flat dict this schema expects."""
        if isinstance(obj, dict):
            return obj
        
        user = getattr(obj, "user", None)
        person = getattr(user, "person", None) if user else None

        return {
            "admin_id": obj.admin_id,
            "user_id": obj.user_id,
            "first_name": person.first_name if person else "",
            "last_name": person.last_name if person else "",
            "phone_number": person.phone_number if person else None,
            "email": user.email if user else None,
            "is_superadmin": obj.is_superadmin,
            "mfa_enabled": getattr(user, "mfa_enabled", False) if user else False,
            "created_at": user.created_at if user else None,
        }

class AdminUpdateProfile(BaseModel):
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None