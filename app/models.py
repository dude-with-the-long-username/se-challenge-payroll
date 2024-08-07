from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from .database import Base
from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.orm import relationship
from datetime import datetime
from pytz import timezone




class FileHash(Base):
    __tablename__ = "file_hash"

    file_hash = Column(String, primary_key=True)


class CSVData(Base):
    __tablename__ = "employee_work"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    hours_worked = Column(Float, nullable=False)
    employee_id = Column(Integer, nullable=False)
    job_group = Column(String, nullable=False)
    half_of_month = Column(Integer, nullable=False)     # finding which half of the month the date is in (expected values: 1 or 2 ie; first half or second half)
    # file_hash_id = Column(String, ForeignKey('file_hash.file_hash'))
    # file_hash = relationship("FileHash")

    def __repr__(self) -> str:
        return f"<EmployeeWork(id={self.id}, date={self.date}, hours_worked={self.hours_worked}, employee_id={self.employee_id}, job_group={self.job_group})>"