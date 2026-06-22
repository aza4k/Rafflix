import hashlib
import hmac
import json
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.config import settings
from core.models import User

def validate_init_data(init_data: str, bot_token: str) -> Dict[str, Any]:
    """
    Validates the initData from Telegram Web App.
    Returns the user data if valid, raises HTTPException otherwise.
    """
    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        if "hash" not in parsed_data:
            raise HTTPException(status_code=401, detail="Missing hash")

        received_hash = parsed_data.pop("hash")
        
        # Sort keys alphabetically
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        # Calculate secret key
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        
        # Calculate validation hash
        expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if received_hash != expected_hash:
            raise HTTPException(status_code=401, detail="Invalid hash")

        # Check for data expiration (optional but recommended, e.g. 24h)
        auth_date = int(parsed_data.get("auth_date", 0))
        if (datetime.utcnow().timestamp() - auth_date) > 86400:
            raise HTTPException(status_code=401, detail="Data expired")

        return parsed_data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=401, detail=f"Invalid initData: {str(e)}")

async def get_db_session():
    from core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency that validates initData and returns the corresponding User from DB.
    """
    init_data = validate_init_data(x_telegram_init_data, settings.BOT_TOKEN)
    
    try:
        user_data = json.loads(init_data.get("user", "{}"))
        tg_id = user_data.get("id")
        if not tg_id:
            raise HTTPException(status_code=401, detail="User ID not found in initData")
            
        res = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = res.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not registered. Please start the bot first.")
            
        return user
    except json.JSONDecodeError:
        raise HTTPException(status_code=401, detail="Invalid user data in initData")
