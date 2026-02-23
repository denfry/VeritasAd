"""Fix NULL values in users table."""
import asyncio
from sqlalchemy import text
from app.models.database import AsyncSessionLocal


async def fix_nulls():
    async with AsyncSessionLocal() as session:
        # Fix total_analyses
        await session.execute(text("UPDATE users SET total_analyses = 0 WHERE total_analyses IS NULL"))
        # Fix daily_used
        await session.execute(text("UPDATE users SET daily_used = 0 WHERE daily_used IS NULL"))
        await session.commit()
        print("✅ NULL values fixed in users table")


if __name__ == "__main__":
    asyncio.run(fix_nulls())
