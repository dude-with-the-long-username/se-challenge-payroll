# Base.py declared as seperate file to avoid circular dependancy in database.py & models.py

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()