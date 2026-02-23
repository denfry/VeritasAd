"""
Migrate existing API keys to hashed format.

This script migrates all existing API keys from the plain text `api_key` column
to the secure `api_key_hash` column.

Usage:
    python scripts/migrate_api_keys.py

Requirements:
    - Database must be migrated (alembic upgrade head)
    - Run this script ONCE before deploying the new code
"""
import asyncio
import hashlib
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import User, get_db, engine
from app.core.dependencies import hash_api_key


async def migrate_api_keys():
    """Migrate all plain text API keys to hashed format."""
    
    print("Starting API key migration...")
    print("=" * 50)
    
    async with AsyncSession(engine) as session:
        # Get all users with API keys
        result = await session.execute(
            select(User).where(User.api_key.isnot(None))
        )
        users_with_keys = result.scalars().all()
        
        if not users_with_keys:
            print("No users with API keys found. Nothing to migrate.")
            return
        
        print(f"Found {len(users_with_keys)} users with API keys")
        print("-" * 50)
        
        migrated_count = 0
        skipped_count = 0
        
        for user in users_with_keys:
            if user.api_key:
                # Check if already migrated (api_key_hash is set)
                if user.api_key_hash:
                    print(f"  SKIP: User {user.id} ({user.email}) - already migrated")
                    skipped_count += 1
                    continue
                
                # Hash the API key
                api_key_hash = hash_api_key(user.api_key)
                
                # Update user record
                await session.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(api_key_hash=api_key_hash)
                )
                
                print(f"  MIGRATED: User {user.id} ({user.email})")
                migrated_count += 1
        
        # Commit all changes
        await session.commit()
        
        print("=" * 50)
        print(f"Migration complete!")
        print(f"  Migrated: {migrated_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Total: {len(users_with_keys)}")
        print()
        print("IMPORTANT: After verifying migration success:")
        print("  1. Deploy the new code (dependencies.py with hash lookup)")
        print("  2. Create a follow-up migration to drop the api_key column")
        print("=" * 50)


if __name__ == "__main__":
    try:
        asyncio.run(migrate_api_keys())
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
