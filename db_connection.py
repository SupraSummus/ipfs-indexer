from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, configure_mappers

import settings

engine = create_engine(settings.DB)
configure_mappers()
Session = sessionmaker(bind=engine)
session = Session()
