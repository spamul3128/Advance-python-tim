import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import BIGINT, VARCHAR, TIMESTAMP, TEXT
from sqlalchemy.sql import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Index
from dotenv import load_dotenv
    
load_dotenv()

# SQLAlchemy declarative base
class Base(DeclarativeBase):
    pass

# ORM Models
class Channel(Base):
    __tablename__ = 'discord_channels'
    
    channel_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    server_id: Mapped[Optional[int]] = mapped_column(BIGINT)
    name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())


class User(Base):
    __tablename__ = 'discord_users'
    
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    username: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    
class Message(Base):
    __tablename__ = 'discord_messages'
    
    message_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BIGINT)
    user_id: Mapped[Optional[int]] = mapped_column(BIGINT)
    content: Mapped[Optional[str]] = mapped_column(TEXT)
    timestamp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    

# Performance indexes
Index('idx_dmsg_channel_id', Message.channel_id)
Index('idx_dmsg_user_id', Message.user_id)
Index('idx_dmsg_timestamp', Message.timestamp)
Index('idx_dchan_server_id', Channel.server_id)

class DatabaseManager:
    """Manages all database operations for the Discord bot using SQLAlchemy"""
    
    def __init__(self):
        self.engine = None
        self.async_session_factory = None
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        # Keep pool attribute for backwards compatibility with existing code
        self.pool = None
    
    async def initialize(self):
        """Initialize database engine and session factory"""
        try:
            # Check if database configuration is complete
            required_vars = ['host', 'database', 'user', 'password']
            missing_vars = [var for var in required_vars if not self.db_config[var]]
            
            if missing_vars:
                print(f"⚠️  Missing database environment variables: {missing_vars}")
                print("⚠️  Bot will run without database functionality")
                return False
            
            # Build database URL
            db_url = (
                f"postgresql+asyncpg://{self.db_config['user']}:{self.db_config['password']}"
                f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            )
            
            # Create async engine
            self.engine = create_async_engine(
                db_url,
                echo=False,  # Set to True for SQL debugging
                pool_size=10,
                max_overflow=20
            )
            
            # Create session factory
            self.async_session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Set pool attribute for backwards compatibility
            self.pool = True  # Just a truthy value to indicate connection is ready
            
            print("✅ Database connection engine created successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to create database engine: {e}")
            return False
    
    async def close(self):
        """Close database engine"""
        if self.engine:
            await self.engine.dispose()
            self.pool = None
            print("Database engine closed.")
    
    @asynccontextmanager
    async def async_session(self):
        """Async context manager for database sessions"""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()
    
    async def create_tables(self):
        """Create all necessary tables using SQLAlchemy metadata"""
        async with self.engine.begin() as conn:
            # Create all tables defined in the metadata
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All database tables created successfully!")
    
    async def ensure_channel_exists(self, channel_id: int, server_id: Optional[int], name: str):
        """Insert channel if it does not already exist"""
        async with self.async_session() as session:
            stmt = insert(Channel).values(
                channel_id=channel_id,
                server_id=server_id,
                name=name
            ).on_conflict_do_nothing(index_elements=[Channel.channel_id])
            await session.execute(stmt)

    async def ensure_user_exists(self, user_id: int, username: str):
        """Insert user if it does not already exist"""
        async with self.async_session() as session:
            stmt = insert(User).values(
                user_id=user_id,
                username=username
            ).on_conflict_do_nothing(index_elements=[User.user_id])
            await session.execute(stmt)

    async def insert_message(self, message_data: Dict[str, Any]):
        """Insert a new message into the database using SQLAlchemy"""
        async with self.async_session() as session:
            # Use insert with on_conflict_do_nothing to avoid duplicate key errors
            stmt = insert(Message).values(
                message_id=message_data['message_id'],
                channel_id=message_data['channel_id'],
                user_id=message_data['user_id'],
                content=message_data['content'],
                timestamp=message_data['timestamp']
            )
            # Prevent duplicate messages if they somehow get processed twice
            stmt = stmt.on_conflict_do_nothing(index_elements=[Message.message_id])
            await session.execute(stmt)
    
    async def get_message_count(self, channel_id: Optional[int] = None) -> int:
        """Get total message count, optionally filtered by channel using SQLAlchemy"""
        async with self.async_session() as session:
            if channel_id:
                stmt = select(func.count()).select_from(Message).where(Message.channel_id == channel_id)
            else:
                stmt = select(func.count()).select_from(Message)
            
            result = await session.scalar(stmt)
            return result or 0
    
    async def get_recent_messages(self, limit: int = 10, channel_id: Optional[int] = None) -> List[Dict]:
        """Get recent messages with join data using SQLAlchemy"""
        async with self.async_session() as session:
            # Build query with left joins
            query = (
                select(
                    Message.message_id,
                    Message.channel_id,
                    Message.user_id,
                    Message.content,
                    Message.timestamp,
                    User.username,
                    Channel.name.label('channel_name')
                )
                .outerjoin(User, Message.user_id == User.user_id)
                .outerjoin(Channel, Message.channel_id == Channel.channel_id)
                .order_by(Message.timestamp.desc())
                .limit(limit)
            )
            
            if channel_id:
                query = query.where(Message.channel_id == channel_id)
            
            result = await session.execute(query)
            rows = result.mappings().all()
            
            # Convert to list of dicts
            return [dict(row) for row in rows]
    
    async def get_messages(
        self,
        user_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        limit: int = 10,
        since: Optional[datetime] = None,
    ) -> List[Dict]:
        """Fetch messages filtered by optional user, channel, and timeframe.

        Results are ordered by Message.timestamp DESC and limited by `limit`.
        """
        async with self.async_session() as session:
            query = (
                select(
                    Message.message_id,
                    Message.channel_id,
                    Message.user_id,
                    Message.content,
                    Message.timestamp,
                    User.username,
                    Channel.name.label('channel_name')
                )
                .outerjoin(User, Message.user_id == User.user_id)
                .outerjoin(Channel, Message.channel_id == Channel.channel_id)
            )

            if user_id:
                query = query.where(Message.user_id == user_id)
            if channel_id:
                query = query.where(Message.channel_id == channel_id)
            if since:
                query = query.where(Message.timestamp >= since)

            query = query.order_by(Message.timestamp.desc()).limit(limit)

            result = await session.execute(query)
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def test_connection(self) -> bool:
        """Test database connection using SQLAlchemy"""
        try:
            async with self.async_session() as session:
                result = await session.scalar(select(func.literal(1)))
                return result == 1
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()
