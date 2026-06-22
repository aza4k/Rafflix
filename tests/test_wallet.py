import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.database import Base
from core.models import User, LedgerType, TicketLedger
from core.wallet import credit_tickets, debit_tickets, InsufficientTicketsError

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_credit_tickets(db_session: AsyncSession):
    # Create a user
    user = User(telegram_id=12345, username="test_user")
    db_session.add(user)
    await db_session.commit()
    
    # Credit tickets
    await credit_tickets(db_session, user.id, 10, LedgerType.PURCHASE, note="Test purchase")
    await db_session.commit()
    
    # Verify balance
    await db_session.refresh(user)
    assert user.ticket_balance == 10
    assert user.total_earned == 10
    
    # Verify ledger
    from sqlalchemy import select
    res = await db_session.execute(select(TicketLedger).where(TicketLedger.user_id == user.id))
    ledger_entry = res.scalar_one()
    assert ledger_entry.amount == 10
    assert ledger_entry.type == LedgerType.PURCHASE
    assert ledger_entry.note == "Test purchase"

@pytest.mark.asyncio
async def test_debit_tickets(db_session: AsyncSession):
    # Create a user with balance
    user = User(telegram_id=67890, username="test_user_debit", ticket_balance=20)
    db_session.add(user)
    await db_session.commit()
    
    # Debit tickets
    await debit_tickets(db_session, user.id, 5, LedgerType.RAFFLE_ENTRY, note="Test entry")
    await db_session.commit()
    
    # Verify balance
    await db_session.refresh(user)
    assert user.ticket_balance == 15
    assert user.total_spent == 5
    
    # Verify ledger
    from sqlalchemy import select
    res = await db_session.execute(select(TicketLedger).where(TicketLedger.user_id == user.id, TicketLedger.amount == -5))
    ledger_entry = res.scalar_one()
    assert ledger_entry.amount == -5
    assert ledger_entry.type == LedgerType.RAFFLE_ENTRY

@pytest.mark.asyncio
async def test_insufficient_tickets(db_session: AsyncSession):
    # Create a user with low balance
    user = User(telegram_id=11111, username="poor_user", ticket_balance=3)
    db_session.add(user)
    await db_session.commit()
    
    # Try to debit more than they have
    with pytest.raises(InsufficientTicketsError):
        await debit_tickets(db_session, user.id, 5, LedgerType.RAFFLE_ENTRY)
