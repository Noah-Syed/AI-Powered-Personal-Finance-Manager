from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import database
import bcrypt

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

from datetime import datetime, timedelta
from uuid import uuid4
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

SECRET_KEY = "change_this_to_a_long_random_secret_key_please"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Allow your React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    jti = str(uuid4())
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # assign a unique JWT ID so we can revoke specific tokens
    to_encode.update({"exp": expire, "jti": jti})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM), jti, expire

def is_token_revoked(db: Session, jti: str) -> bool:
    return db.query(models.RevokedToken).filter(models.RevokedToken.jti == jti).first() is not None

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Save user
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pw.decode('utf-8'))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Signup successful", "user_id": new_user.id, "username": new_user.username}

@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token_data = {"sub": str(user.id), "username": user.username}
    token, jti, exp = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer", "expires_at": exp}

@app.get("/me")
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        jti = payload.get("jti")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if is_token_revoked(db, jti):
        raise HTTPException(status_code=401, detail="Token revoked")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user.id, "username": user.username, "email": user.email}

from fastapi import Header

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check if token has been revoked (logout)
    if jti is not None:
        revoked = db.query(models.RevokedToken).filter(models.RevokedToken.jti == jti).first()
        if revoked is not None:
            raise HTTPException(status_code=401, detail="Token has been revoked")

    user = db.query(models.User).get(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/logout")
def logout(data: dict, db: Session = Depends(get_db)):
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token missing")

    try:
        payload = decode_token(token)
        jti = payload.get("jti")
        exp = payload.get("exp")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

    if not jti:
        raise HTTPException(status_code=400, detail="Invalid token structure")

    # Add revoked token to DB
    if not is_token_revoked(db, jti):
        db_revoked = models.RevokedToken(jti=jti, expires_at=datetime.utcfromtimestamp(exp))
        db.add(db_revoked)
        db.commit()

    return {"message": "Logged out successfully"}

@app.get("/dashboard")
def get_dashboard(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user.username}!"}

# The old login endpoint has been replaced with the OAuth2PasswordRequestForm version above.

# @app.post("/login")
# def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.email == user.email).first()
#     if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#     return {"message": "Login successful", "user_id": db_user.id}
