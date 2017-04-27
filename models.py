from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
import datetime

import settings

Base = declarative_base()


class Name(Base):
    """IPNS name."""
    __tablename__ = 'name'

    hash = Column(String, primary_key=True)

    resolutions = relationship('Resolution')
    references = relationship('NameReference')

    def __str__(self):
       return self.hash


class Resolution(Base):
    """Result of name resolution done at given time."""
    __tablename__ = 'resolution'

    time = Column(DateTime, default=datetime.datetime.utcnow,  primary_key=True)
    name_hash = Column(String, ForeignKey('name.hash'), primary_key=True)
    object_hash = Column(String, ForeignKey('object.hash')) # None if lookup failed


class NameReference(Base):
    """Reference from object to name."""
    __tablename__ = 'name_reference'

    object_hash = Column(String, ForeignKey('object.hash'), primary_key=True)
    type = Column(String, primary_key=True) # reference type
    name_hash = Column(String, ForeignKey('name.hash'), primary_key=True)
    label = Column(String, primary_key=True) # link text


class Object(Base):
    """IPFS object. Probably a dir or a file."""
    __tablename__ = 'object'

    hash = Column(String, primary_key=True)

    properties = relationship('Property')
    availability = relationship('Availability')
    children = relationship('Link', foreign_keys='Link.parent_object_hash')
    parents = relationship('Link', foreign_keys='Link.child_object_hash')
    resolutions = relationship('Resolution')
    referenced_names = relationship('NameReference')


class Property(Base):
    """Property of an object."""
    __tablename__ = 'property'

    object_hash = Column(String, ForeignKey('object.hash'), primary_key=True)
    name = Column(String, primary_key=True)
    value = Column(String) # can be None


class Availability(Base):
    """Info if object was available at given time."""
    __tablename__ = 'availability'

    object_hash = Column(String, ForeignKey('object.hash'), primary_key=True)
    time = Column(DateTime, default=datetime.datetime.utcnow,  primary_key=True)
    available = Column(Boolean)


class Link(Base):
    """Link from one object to another."""
    __tablename__ = 'link'

    type = Column(String, primary_key=True)
    parent_object_hash = Column(String, ForeignKey('object.hash'), primary_key=True)
    child_object_hash = Column(String, ForeignKey('object.hash'), primary_key=True)
    name = Column(String, primary_key=True)



engine = create_engine(settings.DB)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
