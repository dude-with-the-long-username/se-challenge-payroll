import pandas as pd
from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/uploadcsv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    df = pd.read_csv(pd.NamedTemporaryFile(delete=False, suffix=".csv").write(contents))

    for _, row in df.iterrows():
        db_record = models.CSVData(
                id = row['column1'],
                date = row['column2'],
                hours_worked = row['column3'],
                employee_id = row['column4'],
                job_group = row['column5']
        )
        db.add(db_record)

    db.commit()

    return {"message": "CSV data uploaded and stored in the database"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)