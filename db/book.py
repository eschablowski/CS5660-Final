from typing import List
import datetime
from typing import Optional
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import sqlalchemy.types as SQLTypes

from .orm_base import Base

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(SQLTypes.Text())
    issued: Mapped[datetime.date] = mapped_column(SQLTypes.Date())
    language: Mapped[str] = mapped_column(SQLTypes.String(2))
    title: Mapped[str] = mapped_column(SQLTypes.String(70))
    authors: Mapped[List[str]] = mapped_column(SQLTypes.PickleType())
    subjects: Mapped[List[str]] = mapped_column(SQLTypes.PickleType())
    locc: Mapped[List[str]] = mapped_column(SQLTypes.PickleType())
    summary: Mapped["Summary"] = relationship(back_populates="book")
    embeddings: Mapped["Embedding"] = relationship(back_populates="book")
    cluster: Mapped[int] = mapped_column(ForeignKey("clusters.id"), nullable=True)
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

from .summaries import Summary
from .embeddings import Embedding
from .cluster import Cluster