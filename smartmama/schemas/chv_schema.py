from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class CHVUpdateProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    profile_photo_url: Optional[str] = None

class CHVResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chv_id: UUID
    user_id: UUID              
    first_name: str            
    last_name: str             
    email: EmailStr            
    phone_number: Optional[str] = None 
    certificate_status: str    
    created_at: datetime