from sqlalchemy import Column, String, DateTime, Integer
import datetime

from models import Base


class Measurement(Base):
    __tablename__ = 'measurement'

    name = Column(String, primary_key=True)
    date = Column(DateTime, primary_key=True, default=datetime.datetime.utcnow)
    value = Column(Integer, nullable=False)
