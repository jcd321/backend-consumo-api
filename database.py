import os

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

SQL_DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("url")
if not SQL_DATABASE_URL:
    raise RuntimeError("DATABASE_URL no esta configurada")

if SQL_DATABASE_URL.startswith("postgres://"):
    SQL_DATABASE_URL = SQL_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQL_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    email = Column(String)
    edad = Column(Integer)
    password_hash = Column(String, nullable=True)


class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2))
    stock = Column(Integer)
    categoria = Column(String)
    fecha_creacion = Column(DateTime)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
