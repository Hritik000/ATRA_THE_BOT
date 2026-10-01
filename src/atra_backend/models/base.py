"""Base Model Class."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'None')})>"
