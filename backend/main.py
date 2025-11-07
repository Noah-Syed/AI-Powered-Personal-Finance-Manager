from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, database
from models import Expense, User, RevokedToken, FinancialGoal, Badge
from schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseOut,
    UserCreate,
    UserUpdate,
    UserOut,
    FinancialGoalOut,
    FinancialGoalCreateViaPeriod,
    FinancialGoalUpdate,
    BadgeCreate,
    BadgeOut,
)
import bcrypt

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from typing import List, Optional
from fastapi import Path, Query

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

# -----------------------------------

def _to_out(u: User) -> UserOut:
    return UserOut.model_validate(u)

def _hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _require_self(target_user_id: int, current_user: User):
    if current_user.id != target_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

def _to_naive_utc(dt: datetime) -> datetime:
    """Normalize datetimes to naive UTC to avoid aware/naive comparisons.
    If aware, convert to UTC and drop tzinfo; if naive, assume UTC.
    """
    if dt is None:
        return None
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

# ----------- CRUD USER (self-only) -----------

# Create user (adminless projects can treat this as an internal alias of /signup)
@app.post("/api/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_api(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already in use")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=409, detail="Username already in use")

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=_hash_pw(payload.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return _to_out(new_user)

# Read user (self)
@app.get("/api/users/{user_id}", response_model=UserOut)
def read_user_api(
    user_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_self(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_out(user)

# Update user (self)
@app.patch("/api/users/{user_id}", response_model=UserOut)
def update_user_api(
    payload: UserUpdate,
    user_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_self(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email and db.query(User).filter(User.email == payload.email, User.id != user_id).first():
        raise HTTPException(status_code=409, detail="Email already in use")
    if payload.username and db.query(User).filter(User.username == payload.username, User.id != user_id).first():
        raise HTTPException(status_code=409, detail="Username already in use")

    if payload.username: user.username = payload.username
    if payload.email: user.email = payload.email
    if payload.password: user.hashed_password = _hash_pw(payload.password)

    db.add(user); db.commit(); db.refresh(user)
    return _to_out(user)

# Delete user (self) — HARD DELETE
@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_api(
    user_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_self(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user); db.commit()
    return

"""
Expenses CRUD
"""
@app.post("/api/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    new_expense = Expense(
        user_id=current_user.id,
        category=payload.category,
        amount=payload.amount,
        date=payload.date or datetime.utcnow(),
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@app.get("/api/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return expense


@app.get("/api/expenses", response_model=List[ExpenseOut])
def list_expenses(
    category: Optional[str] = Query(default=None),
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Expense).filter(Expense.user_id == current_user.id)

    if category:
        query = query.filter(Expense.category == category)
    if start_date and end_date:
        query = query.filter(Expense.date.between(start_date, end_date))
    elif start_date:
        query = query.filter(Expense.date >= start_date)
    elif end_date:
        query = query.filter(Expense.date <= end_date)

    expenses = query.order_by(Expense.date.desc()).all()
    return expenses or []


@app.patch("/api/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if payload.amount is not None and payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    if payload.category: expense.category = payload.category
    if payload.amount: expense.amount = payload.amount
    if payload.date: expense.date = payload.date

    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@app.delete("/api/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}

"""
Financial Goals CRUD
"""

@app.post("/api/goals", response_model=FinancialGoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: FinancialGoalCreateViaPeriod,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_amount = payload.target_amount
    period_days = payload.period
    if target_amount <= 0:
        raise HTTPException(status_code=400, detail="target_amount must be positive")
    if period_days <= 0:
        raise HTTPException(status_code=400, detail="period must be a positive number of days")

    start_dt = _to_naive_utc(payload.start_date) if payload.start_date else datetime.utcnow()
    end_dt = start_dt + timedelta(days=period_days)
    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    goal = FinancialGoal(
        user_id=current_user.id,
        target_savings=target_amount,
        start_date=start_dt,
        end_date=end_dt,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@app.get("/api/goals", response_model=List[FinancialGoalOut])
def list_goals(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    query = db.query(FinancialGoal).filter(FinancialGoal.user_id == current_user.id)

    if status_filter is not None:
        allowed = {"active", "past"}
        if status_filter not in allowed:
            raise HTTPException(status_code=400, detail="status must be 'active' or 'past'")
        if status_filter == "active":
            query = query.filter(FinancialGoal.start_date <= now, FinancialGoal.end_date >= now)
        elif status_filter == "past":
            query = query.filter(FinancialGoal.end_date < now)

    goals = query.order_by(FinancialGoal.start_date.desc()).all()
    return goals or []


@app.get("/api/goals/{goal_id}", response_model=FinancialGoalOut)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return goal


@app.patch("/api/goals/{goal_id}", response_model=FinancialGoalOut)
def update_goal(
    goal_id: int,
    payload: FinancialGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if payload.target_savings is not None and payload.target_savings <= 0:
        raise HTTPException(status_code=400, detail="target_savings must be positive")

    new_start = _to_naive_utc(payload.start_date) if payload.start_date is not None else goal.start_date
    new_end = _to_naive_utc(payload.end_date) if payload.end_date is not None else goal.end_date

    if new_end <= new_start:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    if payload.target_savings is not None:
        goal.target_savings = payload.target_savings
    if payload.start_date is not None:
        goal.start_date = new_start
    if payload.end_date is not None:
        goal.end_date = new_end

    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@app.delete("/api/goals/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully"}


"""
CREATE BADGE (Manual creation)
"""

@app.post("/api/badges/create", response_model=BadgeOut, status_code=status.HTTP_201_CREATED)
def create_badge(
    payload: BadgeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ensure badges are only created for the current user
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot create badge for another user")

    new_badge = Badge(
        user_id=current_user.id,
        badge_name=payload.badge_name,
        date=payload.date or datetime.utcnow(),
    )
    db.add(new_badge)
    db.commit()
    db.refresh(new_badge)
    return new_badge


"""
# AUTO AWARD BADGE IF WEEKLY SAVINGS MET
"""

@app.post("/api/badges/award", response_model=List[BadgeOut])
def award_badge_if_weekly_savings_met(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)

    # Step 1: Find the user's active financial goal
    goal = (
        db.query(FinancialGoal)
        .filter(
            FinancialGoal.user_id == current_user.id,
            FinancialGoal.start_date <= now,
            FinancialGoal.end_date >= now,
        )
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="No active financial goal found")

    # Step 2: Calculate total spent in the last 7 days
    total_spent = (
        db.query(func.sum(Expense.amount))
        .filter(
            Expense.user_id == current_user.id,
            Expense.date >= week_start,
            Expense.date <= now,
        )
        .scalar()
        or 0
    )

    # Step 3: Compare against savings target
    savings_goal = goal.target_savings
    actual_savings = max(0, savings_goal - total_spent)

    # Step 4: Award badges based on achievements
    earned_badges = []
    badge_definitions = [
        ("Savings Starter", actual_savings >= savings_goal * 0.5),
        ("Goal Crusher", actual_savings >= savings_goal),
        ("Consistency Champ", actual_savings >= savings_goal and now.weekday() == 6),
    ]

    for badge_name, condition in badge_definitions:
        if condition:
            # Prevent duplicates
            existing = (
                db.query(Badge)
                .filter(Badge.user_id == current_user.id, Badge.badge_name == badge_name)
                .first()
            )
            if not existing:
                new_badge = Badge(
                    user_id=current_user.id,
                    badge_name=badge_name,
                    date=datetime.utcnow(),
                )
                db.add(new_badge)
                db.commit()
                db.refresh(new_badge)
                earned_badges.append(new_badge)

    if not earned_badges:
        raise HTTPException(status_code=200, detail="No new badges earned this week")

    return earned_badges