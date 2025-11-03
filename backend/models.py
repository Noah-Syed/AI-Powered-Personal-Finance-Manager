from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    # JWT ID (jti) to uniquely identify a token
    jti = Column(String, unique=True, index=True, nullable=False)
    # When the token naturally expires; useful for housekeeping
    expires_at = Column(DateTime, nullable=False, default=datetime.utcnow)
