from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from app.Utils.logger import setup_logger

# Set up logger
logger = setup_logger()

# Log database URL for confirmation (do not log full credentials in real apps)
logger.info("Initializing database engine")

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Log engine creation
logger.info("Database engine created successfully")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# log session factory creation
logger.info("SessionLocal factory configured")
