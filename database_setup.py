import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Brand(Base):
    __tablename__ = 'brand'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    brand_model = relationship('BrandModel', cascade='all, delete-orphan')

    @property
    def serialize(self):
        """Return data with serialize format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class BrandModel(Base):
    __tablename__ = 'brand_model'

    name = Column(String(80), nullable=False)
    description = Column(String(250))
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('brand.id'))
    brand = relationship(Brand)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return data with serialize format"""
        return {
            'name': self.name,
            'brand': self.brand.name,
            'description': self.description,
        }


engine = create_engine('sqlite:///carsmodel.db')
Base.metadata.create_all(engine)
