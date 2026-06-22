import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Enum, Float, BigInteger, UniqueConstraint, Text
)
from sqlalchemy.orm import Relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base

class RaffleStatus(str, PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DRAWING = "drawing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class LedgerType(str, PyEnum):
    PURCHASE = "purchase"
    REFERRAL = "referral"
    ADMIN_GRANT = "admin_grant"
    STREAK_BONUS = "streak_bonus"
    RAFFLE_ENTRY = "raffle_entry"

class ReferralStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REWARDED = "rewarded"

class TransactionStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64))
    full_name: Mapped[Optional[str]] = mapped_column(String(256))
    referred_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    ticket_balance: Mapped[int] = mapped_column(Integer, default=0)
    total_earned: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[int] = mapped_column(Integer, default=0)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    inviter: Mapped[Optional["User"]] = Relationship("User", remote_side=[id], foreign_keys=[referred_by], back_populates="referred_users")
    referred_users: Mapped[List["User"]] = Relationship("User", remote_side=[referred_by], foreign_keys=[referred_by], back_populates="inviter")
    entries = Relationship("RaffleEntry", back_populates="user")
    ledger_entries = Relationship("TicketLedger", back_populates="user", foreign_keys="[TicketLedger.user_id]")

class Raffle(Base):
    __tablename__ = "raffles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(256))
    gift_name: Mapped[str] = mapped_column(String(256))
    gift_price: Mapped[int] = mapped_column(Integer, nullable=False)
    ticket_price: Mapped[int] = mapped_column(Integer, default=1)
    multiplier: Mapped[float] = mapped_column(Float, default=3.0)
    target_stars: Mapped[int] = mapped_column(Integer)
    collected_stars: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[RaffleStatus] = mapped_column(Enum(RaffleStatus), default=RaffleStatus.DRAFT)
    winner_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    winner = Relationship("User", foreign_keys=[winner_id])
    creator = Relationship("User", foreign_keys=[created_by])
    entries = Relationship("RaffleEntry", back_populates="raffle")

class TicketLedger(Base):
    __tablename__ = "ticket_ledger"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[LedgerType] = mapped_column(Enum(LedgerType), nullable=False)
    ref_raffle_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("raffles.id"))
    ref_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    note: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = Relationship("User", back_populates="ledger_entries", foreign_keys=[user_id])
    ref_user: Mapped[Optional["User"]] = Relationship("User", foreign_keys=[ref_user_id])

class RaffleEntry(Base):
    __tablename__ = "raffle_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raffle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("raffles.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    tickets_used: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('raffle_id', 'user_id', name='_raffle_user_uc'),)

    raffle = Relationship("Raffle", back_populates="entries")
    user = Relationship("User", back_populates="entries")

class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    referred_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    raffle_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("raffles.id"))
    status: Mapped[ReferralStatus] = mapped_column(Enum(ReferralStatus), default=ReferralStatus.PENDING)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    telegram_payment_charge_id: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    stars_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    tickets_granted: Mapped[int] = mapped_column(Integer, nullable=False)
    raffle_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("raffles.id"))
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
