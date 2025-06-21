from pydantic import BaseModel, field_validator, HttpUrl
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

#Enums

class ClaimStatus(str, Enum):
    """
    Enumeration for different statuses a claim can have.
    """
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"

class TaskStatus(str, Enum):
    """
    Enumeration for various stages of a background task.
    """
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

#UserSchema

class UserBase(BaseModel):
    """
    Base user schema containing shared fields.
    """
    username: str

class UserCreate(UserBase):
    """
    Schema for creating a new user. Includes password validation.
    """
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    """
    username: str
    password: str

class UserResponse(UserBase):
    """
    Schema returned after successful user registration or fetch.
    """
    id: int

    model_config = {
        "from_attributes": True  # Allows ORM compatibility
    }

class Token(BaseModel):
    """
    Schema for JWT token response.
    """
    access_token: str
    token_type: str

#Claim Schema

class ClaimBase(BaseModel):
    """
    Shared base schema for a healthcare claim.
    Includes field-level validation.
    """
    patient_name: str
    diagnosis_code: str
    procedure_code: str
    claim_amount: Decimal

    @field_validator('patient_name')
    @classmethod
    def validate_patient_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Patient name is required')
        return v.strip()

    @field_validator('diagnosis_code')
    @classmethod
    def validate_diagnosis_code(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Diagnosis code is required')
        return v.strip()

    @field_validator('procedure_code')
    @classmethod
    def validate_procedure_code(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Procedure code is required')
        return v.strip()

    @field_validator('claim_amount')
    @classmethod
    def validate_claim_amount(cls, v):
        if v <= 0:
            raise ValueError('Claim amount must be greater than 0')
        return v

class ClaimCreate(ClaimBase):
    """
    Schema for creating a new claim.
    Inherits validations from ClaimBase.
    """
    pass

class ClaimUpdate(BaseModel):
    """
    Schema for updating the status of a claim.
    """
    status: ClaimStatus

class ClaimResponse(ClaimBase):
    """
    Schema for a full claim response including ID and status.
    """
    id: int
    status: ClaimStatus
    submitted_at: datetime

    model_config = {
        "from_attributes": True
    }

class ClaimListResponse(BaseModel):
    """
    Schema for paginated list of claims.
    """
    claims: List[ClaimResponse]
    total: int
    skip: int
    limit: int

#Reports Schema
class ReportBase(BaseModel):
    """
    Base schema for report task information.
    Used for both status checks and download.
    """
    task_id: str
    status: TaskStatus
    download_url: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    created_by: Optional[str] = None

class ReportTaskResponse(ReportBase):
    """
    Schema returned immediately after starting a report generation task.
    """
    message: Optional[str] = None

class ReportStatusResponse(ReportBase):
    """
    Schema for checking the current status of a report task.
    """
    pass


class BulkUploadResponse(BaseModel):
    """
    Schema for response after bulk claim upload.
    """
    total_processed: int
    successful_uploads: int
    failed_uploads: int
    successes: List[dict]
    errors: List[dict]

class WebhookRegister(BaseModel):
    """
    Schema to register a webhook for task completion callbacks.
    """
    task_id: str
    url: HttpUrl
