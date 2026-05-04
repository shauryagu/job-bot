"""
Database Session Module

Manages database sessions and connections with PostgreSQL connection pooling
optimized for 1000 concurrent users.

Supports both synchronous and asynchronous database operations.
"""

from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import get_logger
from app.db.postgres_config import postgres_config

logger = get_logger(__name__)

# Determine which database to use based on configuration
# Priority: PostgreSQL (production) > SQLite (development)
use_postgres = bool(settings.postgres_password)  # If password is set, use PostgreSQL

if use_postgres:
    # PostgreSQL Configuration
    logger.info("Using PostgreSQL database with connection pooling")

    # Synchronous engine for traditional SQLAlchemy
    engine = create_engine(
        postgres_config.database_url,
        echo=settings.database_echo,
        **postgres_config.pool_config,
        **postgres_config.connection_kwargs,
    )

    # Asynchronous engine for async SQLAlchemy
    async_engine = create_async_engine(
        postgres_config.database_url_async,
        echo=settings.database_echo,
        **postgres_config.pool_config,
    )

    # Session factories
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    AsyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

else:
    # SQLite Configuration (development/fallback)
    logger.warning(
        "Using SQLite database - NOT recommended for production or 1000+ users. "
        "Set POSTGRES_PASSWORD in .env to enable PostgreSQL."
    )

    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,
    )

    # SQLite doesn't support asyncpg, use aiosqlite for async
    async_database_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
    async_engine = create_async_engine(
        async_database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,
    )

    # Session factories
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    AsyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def get_db() -> Generator[Session, None, None]:
    """
    Get synchronous database session.

    Yields:
        Database session

    Usage:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get asynchronous database session.

    Yields:
        Async database session

    Usage:
        @app.get("/")
        async def endpoint(db: AsyncSession = Depends(get_async_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


def init_db() -> None:
    """
    Initialize database connection.

    This function tests the database connection and logs the result.
    """
    try:
        with engine.connect() as conn:
            logger.info("Database connection established successfully")

            # Log connection pool status if using PostgreSQL
            if use_postgres:
                pool = engine.pool
                logger.info(
                    f"Connection pool status: "
                    f"size={pool.size()}, "
                    f"checked_in={pool.checkedin()}, "
                    f"checked_out={pool.checkedout()}, "
                    f"overflow={pool.overflow()}"
                )
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def init_async_db() -> None:
    """
    Initialize asynchronous database connection.

    This function tests the async database connection and logs the result.
    """
    try:
        async with async_engine.connect() as conn:
            logger.info("Async database connection established successfully")

            # Log connection pool status if using PostgreSQL
            if use_postgres:
                pool = async_engine.pool
                logger.info(
                    f"Async connection pool status: "
                    f"size={pool.size()}, "
                    f"checked_in={pool.checkedin()}, "
                    f"checked_out={pool.checkedout()}, "
                    f"overflow={pool.overflow()}"
                )
    except Exception as e:
        logger.error(f"Failed to connect to async database: {e}")
        raise


def check_db_health() -> dict:
    """
    Check database health and return status information.

    Returns:
        Dictionary with health status and connection pool information
    """
    try:
        with engine.connect() as conn:
            # Execute simple query
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

            health_status = {
                "status": "healthy",
                "database": "postgresql" if use_postgres else "sqlite",
                "connection": "ok",
            }

            # Add pool information for PostgreSQL
            if use_postgres:
                pool = engine.pool
                health_status["pool"] = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "max_overflow": postgres_config.postgres_max_overflow,
                }

                # Check if pool is under pressure
                total_connections = pool.size() + pool.overflow()
                used_connections = pool.checkedout()
                utilization = used_connections / total_connections if total_connections > 0 else 0

                health_status["pool"]["utilization"] = f"{utilization:.1%}"

                if utilization > 0.8:
                    logger.warning(
                        f"Connection pool utilization high: {utilization:.1%}. "
                        "Consider increasing pool size."
                    )

            return health_status

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "postgresql" if use_postgres else "sqlite",
            "connection": "failed",
            "error": str(e),
        }


async def check_async_db_health() -> dict:
    """
    Check async database health and return status information.

    Returns:
        Dictionary with health status and connection pool information
    """
    try:
        async with async_engine.connect() as conn:
            # Execute simple query
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()

            health_status = {
                "status": "healthy",
                "database": "postgresql" if use_postgres else "sqlite",
                "connection": "ok",
            }

            # Add pool information for PostgreSQL
            if use_postgres:
                pool = async_engine.pool
                health_status["pool"] = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "max_overflow": postgres_config.postgres_max_overflow,
                }

                # Check if pool is under pressure
                total_connections = pool.size() + pool.overflow()
                used_connections = pool.checkedout()
                utilization = used_connections / total_connections if total_connections > 0 else 0

                health_status["pool"]["utilization"] = f"{utilization:.1%}"

                if utilization > 0.8:
                    logger.warning(
                        f"Async connection pool utilization high: {utilization:.1%}. "
                        "Consider increasing pool size."
                    )

            return health_status

    except Exception as e:
        logger.error(f"Async database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "postgresql" if use_postgres else "sqlite",
            "connection": "failed",
            "error": str(e),
        }
