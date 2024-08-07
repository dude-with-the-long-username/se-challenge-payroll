from sqlalchemy import Column, Integer, String, Float
from .database import Base
from sqlalchemy.sql.sqltypes import Date

class CSVData(Base):
    __tablename__ = "employee_work"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    hours_worked = Column(Float, nullable=False)
    employee_id = Column(Integer, nullable=False)
    job_group = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"<EmployeeWork(id={self.id}, date={self.date}, hours_worked={self.hours_worked}, employee_id={self.employee_id}, job_group={self.job_group})>"