"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import os

from .models import Base


class DatabaseManager:
    """Manage SQLite database connections and initialization."""
    
    def __init__(self, db_path: str = "mental_health_monitor.db"):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Create absolute path if relative
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path)
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
        """Initialize database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session.
        
        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()


# Global instance
_db_manager: Optional[DatabaseManager] = None


def init_database(db_path: str = "mental_health_monitor.db") -> DatabaseManager:
    """Initialize the global database manager.
    
    Args:
        db_path: Path to SQLite database file
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    _db_manager = DatabaseManager(db_path)
    _db_manager.init_db()
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """Get the global database manager.
    
    Returns:
        DatabaseManager instance
    
    Raises:
        RuntimeError: If database manager not initialized
    """
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db_manager


def get_session() -> Session:
    """Get a database session from the global manager.
    
    Returns:
        SQLAlchemy Session object
    """
    return get_db_manager().get_session()
