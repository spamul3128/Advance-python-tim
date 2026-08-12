#!/usr/bin/env python3
"""
Database Initialization Script for DevLaunch Discord Bot
This script sets up the database schema and tests the connection.
"""

import asyncio
from dotenv import load_dotenv
from datetime import datetime, UTC
from database import db_manager

async def main():
    """Initialize the database"""
    print("🚀 Starting database initialization...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize database connection
    success = await db_manager.initialize()
    if not success:
        print("❌ Failed to initialize database connection. Exiting.")
        return
    
    # Test connection
    print("🔍 Testing database connection...")
    if not await db_manager.test_connection():
        print("❌ Database connection test failed. Exiting.")
        await db_manager.close()
        return
    
    print("✅ Database connection test passed!")
    
    # Create tables
    print("📋 Creating database tables...")
    try:
        await db_manager.create_tables()
        print("✅ Database schema created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        await db_manager.close()
        return
    
    # Test data insertion (optional)
    print("🧪 Testing basic database operations...")
    try:
        # Test insert-only channel & user
        await db_manager.ensure_channel_exists(
            channel_id=111222333,
            server_id=123456789,
            name="test-channel",
        )
        await db_manager.ensure_user_exists(
            user_id=555666777,
            username="testuser",
        )

        # Insert a simple text message
        await db_manager.insert_message({
            'message_id': 999888777,
            'channel_id': 111222333,
            'user_id': 555666777,
            'content': 'hello world',
            'timestamp': datetime.now(UTC),
        })

        print("✅ Basic database operations test passed!")
        
        # Get message count
        count = await db_manager.get_message_count()
        print(f"📊 Current message count in database: {count}")
        
    except Exception as e:
        print(f"❌ Error testing database operations: {e}")
    
    # Close database connection
    await db_manager.close()
    print("🏁 Database initialization completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
