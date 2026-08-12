#!/usr/bin/env python3
import asyncio
from sqlalchemy import text
from database import Base, DatabaseManager

async def main():
    mgr = DatabaseManager()
    ok = await mgr.initialize()
    if not ok or mgr.engine is None:
        print("❌ Database not configured. Set DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD.")
        return

    print("⚠️ Dropping tables (if exist)...")
    async with mgr.engine.begin() as conn:
        for tbl in [
            "server_members",
            "messages",
            "channels",
            "users",
            "servers",
            "discord_messages",
            "discord_channels",
            "discord_users",
        ]:
            await conn.execute(text(f'DROP TABLE IF EXISTS {tbl} CASCADE'))
    print("✅ All known tables dropped.")

    print("🛠️ Recreating tables with new schema...")
    async with mgr.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Schema recreated.")

    await mgr.close()

if __name__ == "__main__":
    asyncio.run(main())

