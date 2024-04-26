from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import Column, Integer, Sequence, String, Text, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from datetime import timedelta

Base = declarative_base()
connection_string = "mysql+pymysql://root:mechanix93@localhost/bot_datamalevich"
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

class Data(Base):
    __tablename__ = 'data'
    user_id = Column(Integer)
    data_time = Column(DateTime)
    gender = Column(String(50))
    age = Column(Integer)
    name = Column(String(50))
    city = Column(String(50))
    experience = Column(String(50))
    target = Column(String(50))
    time_talk = Column(String(50))
    phone = Column(String(50))
    nickname = Column(String(50))
    posted = Column(Integer)
    __table_args__ = (PrimaryKeyConstraint(user_id, data_time), {},)

Base.metadata.create_all(engine)