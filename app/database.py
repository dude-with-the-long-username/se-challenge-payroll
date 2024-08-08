from sqlalchemy import create_engine
from .base import Base
from sqlalchemy.orm import sessionmaker
from .models import HourlyRates
from sqlalchemy.exc import ProgrammingError

SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

def create_hourly_rates_table():
    try:
        Base.metadata.create_all(bind=engine)
        session = SessionLocal()
        
        # Check if the hourly_rates table is empty
        if session.query(HourlyRates).count() == 0:
            # Populate the hourly_rates table with initial data
            session.add_all([
                HourlyRates(job_group='A', hourly_rate=20),
                HourlyRates(job_group='B', hourly_rate=30)
            ])
            session.commit()
    except ProgrammingError:
        # Ignore the error if the hourly_rates table already exists
        pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()