import json
from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from core.models import User, Transaction, TransactionStatus, LedgerType, Referral, ReferralStatus
from core.wallet import credit_tickets
from core.config import settings

router = Router()

@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message, db_session: AsyncSession):
    payment = message.successful_payment
    if not payment:
        return

    # Payload is usually a JSON string we sent in the invoice
    try:
        payload = json.loads(payment.invoice_payload)
    except (json.JSONDecodeError, TypeError):
        payload = {}

    # 1. Get User
    res = await db_session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = res.scalar_one_or_none()
    
    if not user:
        return # Should not happen if they used the bot

    # 2. Record Transaction
    raffle_id = payload.get("raffle_id")
    if raffle_id:
        try:
            raffle_id = uuid.UUID(raffle_id)
        except ValueError:
            raffle_id = None

    transaction = Transaction(
        user_id=user.id,
        telegram_payment_charge_id=payment.telegram_payment_charge_id,
        stars_amount=payment.total_amount, # In XTR
        tickets_granted=payment.total_amount, # 1 Star = 1 Ticket
        raffle_id=raffle_id,
        status=TransactionStatus.COMPLETED
    )
    db_session.add(transaction)

    # 2.5 Update Raffle Collected Stars
    if raffle_id:
        await db_session.execute(
            update(Raffle)
            .where(Raffle.id == raffle_id)
            .values(collected_stars=Raffle.collected_stars + payment.total_amount)
        )

    # 3. Credit Tickets
    await credit_tickets(
        db_session, 
        user.id, 
        payment.total_amount, 
        LedgerType.PURCHASE,
        note=f"Bought {payment.total_amount} tickets"
    )

    # 4. Referral Confirmation (Only on first purchase)
    if user.total_earned == payment.total_amount: # This was their first credit
        res = await db_session.execute(
            select(Referral).where(Referral.referred_id == user.id, Referral.status == ReferralStatus.PENDING)
        )
        referral = res.scalar_one_or_none()
        
        if referral:
            referral.status = ReferralStatus.REWARDED
            # Credit referrer
            await credit_tickets(
                db_session,
                referral.referrer_id,
                1,
                LedgerType.REFERRAL,
                ref_user_id=user.id,
                note="Referral bonus"
            )
            
            # Notify referrer (if possible, but we don't have bot object here easily without middleware or global)
            # For now just update DB, we can add notification logic in bot/utils/notifications.py later

    await db_session.commit()
    
    await message.answer(
        f"✅ <b>Payment successful!</b>\n\n"
        f"You received <b>{payment.total_amount}</b> tickets. "
        "Your balance has been updated. Go enter some raffles! 🚀"
    )
