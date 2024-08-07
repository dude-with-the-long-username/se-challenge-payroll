import pandas as pd
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import tempfile
import os
from datetime import datetime
import hashlib

from .database import engine, get_db
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def cast_csv_data(row):
    try:
        return {
            'date': pd.to_datetime(row['date']).date(),
            'hours_worked': float(row['hours worked']),
            'employee_id': int(row['employee id']),
            'job_group': str(row['job group']).strip().upper()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)