from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

from db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String, unique=False, index=True)
    hashed = Column(String, unique=True, index=True)
    processed_image_path = Column(String, unique=False, index=True)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    x1 = Column(Float)
    y1 = Column(Float)
    x2 = Column(Float)
    y2 = Column(Float)
    photo_id = Column(Integer, ForeignKey('images.id'))

    # Добавляем связь с моделью Image
    image = relationship("Image")



