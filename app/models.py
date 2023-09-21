from sqlalchemy import Column, Integer, String, REAL, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Greeting(Base):
    __tablename__ = "greetings"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String, unique=True, index=True)
    hashed = Column(String, unique=True, index=True)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    x1 = Column(REAL)
    y1 = Column(REAL)
    x2 = Column(REAL)
    y2 = Column(REAL)
    photo_id = Column(Integer, ForeignKey('images.id'))

    # Добавляем связь с моделью Image
    image = relationship("Image")