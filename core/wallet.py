import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from core.models import User, TicketLedger, LedgerType

class InsufficientTicketsError(Exception):
    """Raised when a user does not have enough tickets for a debit operation."""
    pass

async def credit_tickets(
    session: AsyncSession,
    user_id: uuid.UUID,
    amount: int,
    ledger_type: LedgerType,
    ref_raffle_id: Optional[uuid.UUID] = None,
    ref_user_id: Optional[uuid.UUID] = None,
    note: str = ""
):
    """
    Credits tickets to a user's balance and records the transaction in the ledger.
    """
    # 1. Update user balance
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            ticket_balance=User.ticket_balance + amount,
            total_earned=User.total_earned + amount
        )
    )
    await session.execute(stmt)

    # 2. Record in ledger
    ledger_entry = TicketLedger(
        user_id=user_id,
        amount=amount,
        type=ledger_type,
        ref_raffle_id=ref_raffle_id,
        ref_user_id=ref_user_id,
        note=note
    )
    session.add(ledger_entry)
    await session.flush()

async def debit_tickets(
    session: AsyncSession,
    user_id: uuid.UUID,
    amount: int,
    ledger_type: LedgerType,
    ref_raffle_id: Optional[uuid.UUID] = None,
    note: str = ""
):
    """
    Debits tickets from a user's balance and records the transaction in the ledger.
    Raises InsufficientTicketsError if balance is too low.
    """
    # 1. Check balance and lock row for update
    result = await session.execute(
        select(User.ticket_balance).where(User.id == user_id).with_for_update()
    )
    balance = result.scalar_one_or_none()

    if balance is None or balance < amount:
        raise InsufficientTicketsError(f"User {user_id} has {balance} tickets, needs {amount}")

    # 2. Update user balance
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            ticket_balance=User.ticket_balance - amount,
            total_spent=User.total_spent + amount
        )
    )
    await session.execute(stmt)

    # 3. Record in ledger
    ledger_entry = TicketLedger(
        user_id=user_id,
        amount=-amount,
        type=ledger_type,
        ref_raffle_id=ref_raffle_id,
        note=note
    )
    session.add(ledger_entry)
    await session.flush()
