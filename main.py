from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import Base, ProductDB, UserDB, engine, get_db
from schemas import (
    LoginRequest,
    Product,
    ProductCreate,
    Token,
    User,
    UserCreate,
    UserRegister,
    UserResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database connection error: {e}")
        # In production, you might want to exit or handle differently
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:4200", 
    "http://127.0.0.1:4200",
    "https://consumo-api-1.netlify.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API is running. Visit /docs for documentation."}


@app.get("/doc")
def redirect_doc_to_docs():
    return RedirectResponse(url="/docs")


@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    email = user_data.email.strip().lower()
    existing = db.query(UserDB).filter(func.lower(UserDB.email) == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    max_id = db.query(func.max(UserDB.id)).scalar()
    next_id = (max_id or 0) + 1
    new_user = UserDB(
        id=next_id,
        nombre=user_data.nombre,
        email=email,
        edad=user_data.edad,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    email = credentials.email.strip().lower()
    user = db.query(UserDB).filter(func.lower(UserDB.email) == email).first()
    if not user or not user.password_hash or not verify_password(
        credentials.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)


@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/users", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()


@app.get("/users/{user_id}", response_model=User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@app.post("/users", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    max_id = db.query(func.max(UserDB.id)).scalar()
    next_id = (max_id or 0) + 1
    new_user = UserDB(
        id=next_id,
        nombre=user.nombre,
        email=user.email,
        edad=user.edad,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db_user.nombre = user.nombre
    db_user.email = user.email
    db_user.edad = user.edad
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"message": f"Usuario con ID {user_id} eliminado exitosamente"}


@app.get("/products", response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()


@app.get("/products/{product_id}", response_model=Product)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@app.post("/products", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    max_id = db.query(func.max(ProductDB.id)).scalar()
    next_id = (max_id or 0) + 1
    new_product = ProductDB(
        id=next_id,
        nombre=product.nombre,
        descripcion=product.descripcion,
        precio=product.precio,
        stock=product.stock,
        categoria=product.categoria,
        fecha_creacion=datetime.now(),
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db_product.nombre = product.nombre
    db_product.descripcion = product.descripcion
    db_product.precio = product.precio
    db_product.stock = product.stock
    db_product.categoria = product.categoria
    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(product)
    db.commit()
    return {"message": f"Producto con ID {product_id} eliminado exitosamente"}
