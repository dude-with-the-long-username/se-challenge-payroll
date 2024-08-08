import pandas as pd
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import tempfile
import os
import hashlib
from .database import create_hourly_rates_table
from .database import engine, get_db
from . import models

models.Base.metadata.create_all(bind=engine)

create_hourly_rates_table() # create hourly_rates table (with rates for job groups A and B)

app = FastAPI()

def cast_csv_data(row):
    try:
        return {
            'date': pd.to_datetime(row['date'], format='%d/%m/%Y', dayfirst=True).date(),
            'hours_worked': float(row['hours worked']),
            'employee_id': int(row['employee id']),
            'job_group': str(row['job group']).strip().upper(),
            'half_of_month': 1 if pd.to_datetime(row['date']).day <= 15 else 2   # calculating which half (first or second) of the month, the date belongs to
        }
    except ValueError as e:
        raise ValueError(f"Error casting data in row {row.name + 2}: {str(e)}")

@app.post("/uploadcsv/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    
    file_hash = hashlib.md5(contents).hexdigest()

    # Check for existing file hash
    existing_file_hash = db.query(models.FileHash).filter_by(file_hash=file_hash).first()
    if existing_file_hash:
        raise HTTPException(status_code=409, detail="Duplicate file entry. File with this content already exists.")

    # Create a new FileHash record
    file_hash_record = models.FileHash(file_hash=file_hash)
    db.add(file_hash_record)


    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(contents)
        temp_file_path = temp_file.name
    
    try:
        df = pd.read_csv(temp_file_path)
        
        for _, row in df.iterrows():
            try:
                casted_data = cast_csv_data(row)
                db_record = models.CSVData(**casted_data)
                db.add(db_record)
            except ValueError as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        
        db.commit()
        return {"message": "CSV data uploaded and stored in the database"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

@app.get("/payroll_report")
async def get_payroll_report(db: Session = Depends(get_db)):

    # SQL query to return output in desired format
    payroll_report_query = """

    SELECT 
        emp.employee_id
        , emp.start_date
        , emp.end_date
        , SUM(emp.hours_worked * hr.hourly_rate) AS total_amount_paid
    FROM
        (
            SELECT
                wd.employee_id,
                CASE WHEN wd.half_of_month = 1 
                        THEN date(wd.date, 'start of month') 
                    ELSE date(wd.date, 'start of month', '+15 days') 
                END AS start_date,
                CASE WHEN wd.half_of_month = 1 
                        THEN date(wd.date, 'start of month', '+14 days') 
                    ELSE date(wd.date, 'start of month', '+1 month', '-1 day') 
                END AS end_date,
                wd.hours_worked,
                wd.job_group
            FROM employee_work wd
        )emp
        INNER JOIN hourly_rates hr 
            ON emp.job_group = hr.job_group
    GROUP BY emp.employee_id
        , emp.start_date
        ,emp.end_date
    ORDER BY emp.employee_id
        , emp.start_date 
    """

    report_data = db.execute(payroll_report_query).fetchall()


    processed_report_data = {
        "payrollReport": {
            "employeeReports": [
                {
                    "employeeId": str(row[0]),  # Convert employee_id to string
                    "payPeriod": {
                        "startDate": row[1],
                        "endDate": row[2]
                    },
                    "amountPaid": f"${row[3]:.2f}"  # Format amount with two decimal places
                }
                for row in report_data
            ]
        }
    }


    return processed_report_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)