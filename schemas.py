from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    nombre: str
    email: str
    edad: int


class UserRegister(BaseModel):
    nombre: str
    email: str
    edad: int
    password: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    edad: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    id: int
    nombre: str
    email: str
    edad: int

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str


class Product(BaseModel):
    id: int
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True
