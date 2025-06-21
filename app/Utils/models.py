from sqlalchemy import Column, Integer, String, DateTime, Enum, Text,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime,timezone
import enum

Base = declarative_base()

class ClaimStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    
#User Data Base
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    
#Claim Data Base
class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_name = Column(String(100), nullable=False)
    diagnosis_code = Column(String(20), nullable=False, index=True)
    procedure_code = Column(String(20), nullable=False, index=True)
    claim_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(ClaimStatus), nullable=False, default=ClaimStatus.PENDING, index=True)
    submitted_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
#Report Database
class ReportTask(Base):
    __tablename__ = "report_tasks"
    
    id = Column(String(36), primary_key=True)  # UUID
    status = Column(String(20), nullable=False, default="PENDING")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    file_path = Column(String(255), nullable=True)
    webhook_url = Column(String(500), nullable=True)