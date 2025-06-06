from pydantic import BaseModel, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    first_name: str
    last_name: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search("[a-z]", v):
            raise ValueError(
                'Password must contain at least one lowercase letter')
        if not re.search("[A-Z]", v):
            raise ValueError(
                'Password must contain at least one uppercase letter')
        return v
    
class UserRead(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True
        
        
class ResetPassword(BaseModel):
    token: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ForgotPassword(BaseModel):
    email: str