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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # assign a unique JWT ID so we can revoke specific tokens
    to_encode.update({"exp": expire, "jti": str(uuid4())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm sends fields as: username=<email_or_username>, password=<password>
    identifier = form_data.username  # allow login by email for now
    user = db.query(models.User).filter(models.User.email == identifier).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

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

@app.get("/me")
def read_me(current_user: models.User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}


@app.post("/logout")
def logout(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Invalidate the current access token by storing its jti in a blacklist.
    Clients should discard the token after calling this endpoint.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp_ts = payload.get("exp")
        if jti is None or exp_ts is None:
            raise HTTPException(status_code=400, detail="Token missing required claims")
        expires_at = datetime.utcfromtimestamp(exp_ts)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # If already revoked, return success (idempotent)
    existing = db.query(models.RevokedToken).filter(models.RevokedToken.jti == jti).first()
    if existing is None:
        revoked = models.RevokedToken(jti=jti, expires_at=expires_at)
        db.add(revoked)
        db.commit()

    return {"message": "Logged out"}

# The old login endpoint has been replaced with the OAuth2PasswordRequestForm version above.

# @app.post("/login")
# def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.email == user.email).first()
#     if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#     return {"message": "Login successful", "user_id": db_user.id}
