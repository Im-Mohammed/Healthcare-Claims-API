from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import csv, os, uuid, io
# Rate limiting 
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
# Importing custom code modules
from .Tasks.tasks import generate_claims_report_task
from .Utils.database import SessionLocal, engine
from .Utils.models import User, Claim, Base
from .Utils.schemas import *
from .Auth.auth import get_password_hash, verify_password, create_access_token, decode_access_token
from .Utils.config import settings
from celery.result import AsyncResult
from fastapi.middleware.cors import CORSMiddleware
from app.Utils.logger import setup_logger
import logging

#Setting up the logger 
setup_logger()

logger = logging.getLogger(__name__)
logger.info("App has started!")

# Automatically create database tables defined in the `models`
Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI(title="Healthcare Claims Processing API")

# Set up rate limiting to prevent abuse
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Enable Cross-Origin Resource Sharing (CORS) so frontend apps can interact with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


security = HTTPBearer()
background_tasks_storage: Dict[str, Dict[str, Any]] = {}
webhook_registry: Dict[str, str] = {}

def get_db():
    """
    Provides a database session for each request and ensures it's closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Extracts user from JWT token and checks if user exists in DB.
    Raises 401 if token is invalid or user doesn't exist.
    """
    try:
        payload = decode_access_token(credentials.credentials)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

@app.post("/auth/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    #Registers a new user
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(400, detail="Username already exists")
    hashed = get_password_hash(user_data.password)
    db_user = User(username=user_data.username, password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Logs user in and returns JWT token.
    """
    user = db.query(User).filter(User.username == user_credentials.username).first()
    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

@app.post("/claims", response_model=ClaimResponse)
@limiter.limit("10/minute")
async def create_claim(request: Request, claim_data: ClaimCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Submits a new claim
    """
    claim = Claim(**claim_data.dict(), status=ClaimStatus.PENDING, submitted_at=datetime.now(timezone.utc))
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim

@app.get("/claims", response_model=ClaimListResponse)
async def get_claims(skip: int = 0, limit: int = 100, status: Optional[ClaimStatus] = None, diagnosis_code: Optional[str] = None, procedure_code: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve a list of submitted claims with optional filters.
    """
    query = db.query(Claim)
    if status:
        query = query.filter(Claim.status == status)
    if diagnosis_code:
        query = query.filter(Claim.diagnosis_code == diagnosis_code)
    if procedure_code:
        query = query.filter(Claim.procedure_code == procedure_code)
    total = query.count()
    claims = query.offset(skip).limit(limit).all()
    return ClaimListResponse(claims=claims, total=total, skip=skip, limit=limit)

@app.get("/claims/{claim_id}", response_model=ClaimResponse)
async def get_claim(claim_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve a specific claim by ID.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(404, "Claim not found")
    return claim

@app.put("/claims/{claim_id}", response_model=ClaimResponse)
async def update_claim(claim_id: int, update: ClaimUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update status of a claim.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(404, "Claim not found")
    claim.status = update.status
    db.commit()
    db.refresh(claim)
    return claim

@app.delete("/claims/{claim_id}")
async def delete_claim(claim_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Delete a claim by ID.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(404, "Claim not found")
    db.delete(claim)
    db.commit()
    return {"message": "Claim deleted"}

@app.post("/claims/bulk")
async def bulk_upload(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Upload multiple claims using a CSV file.
    """
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    success = 0
    errors = []
    for i, row in enumerate(reader, start=1):
        try:
            claim = Claim(
                patient_name=row["patient_name"],
                diagnosis_code=row["diagnosis_code"],
                procedure_code=row["procedure_code"],
                claim_amount=float(row["claim_amount"]),
                status=ClaimStatus.PENDING,
                submitted_at=datetime.now(timezone.utc)
            )
            db.add(claim)
            success += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e)})
    db.commit()
    return {"message": "Bulk upload completed", "successful_uploads": success, "errors": errors}

@app.post("/claims/report", response_model=ReportTaskResponse)
async def generate_report(current_user: User = Depends(get_current_user)):   
    """
    Start generating a claims report in the background using Celery.
    """
    task_id = str(uuid.uuid4())
    webhook_url = webhook_registry.get(current_user.username)
    
    # Launch celery task
    result = generate_claims_report_task.delay(task_id, current_user.username, webhook_url)

    # Save tracking info
    background_tasks_storage[task_id] = {
        "status": TaskStatus.PENDING.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "celery_id": result.id,
        "created_by": current_user.username
    }

    return ReportTaskResponse(task_id=task_id, status=TaskStatus.PENDING, message="Report started")



@app.get("/claims/report/{task_id}", response_model=ReportStatusResponse)
async def get_report_status(task_id: str, current_user: User = Depends(get_current_user)):
    """
    Check the status of a report generation task.
    """
    task_info = background_tasks_storage.get(task_id)
    if not task_info:
        raise HTTPException(404, "Task not found")

    celery_id = task_info.get("celery_id")
    result = AsyncResult(celery_id)

    if result.failed():
        status = TaskStatus.FAILED

    elif result.successful():
        status = TaskStatus.COMPLETED  
        output = result.result
        task_info.update({
            "file_path": output.get("file_path"),
            "completed_at": output.get("completed_at")
        })

    elif result.status == "STARTED":
        status = TaskStatus.PROCESSING
    else:
        status = TaskStatus.PENDING

    task_info["status"] = status.value
    return ReportStatusResponse(task_id=task_id, **task_info)



@app.get("/claims/report/{task_id}/download")
async def download_report(task_id: str, current_user: User = Depends(get_current_user)):
    """
    Download the generated report once completed.
    """
    task = background_tasks_storage.get(task_id)
    if not task or task["status"] != TaskStatus.COMPLETED.value:
        raise HTTPException(404, "Report not ready")
    return FileResponse(task["file_path"], filename=f"claims_report_{task_id}.csv")

@app.post("/webhook")
async def register_webhook(url: WebhookRegister, current_user: User = Depends(get_current_user)):
    """
    Register a webhook to be notified when reports are ready.
    """
    webhook_registry[current_user.username] = url.url
    return {"message": "Webhook registered"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}
