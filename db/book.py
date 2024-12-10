from typing import List
import datetime
from typing import Optional
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import sqlalchemy.types as SQLTypes

from .orm_base import Base


book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book", ForeignKey("books.id")),
    Column("author", ForeignKey("authors.id")),
)
book_subjects = Table(
    "book_subjects",
    Base.metadata,
    Column("book", ForeignKey("books.id")),
    Column("subject", ForeignKey("subjects.id")),
)
book_locc = Table(
    "book_locc",
    Base.metadata,
    Column("book", ForeignKey("books.id")),
    Column("LoCC", ForeignKey("LoCC.id")),
)

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    issued: Mapped[datetime.date] = mapped_column(SQLTypes.Date())
    language: Mapped[str] = mapped_column(SQLTypes.String(2))
    title: Mapped[str] = mapped_column(SQLTypes.String(70))
    authors: Mapped[List["Author"]] = relationship(secondary=book_authors)
    subjects: Mapped[List["Subject"]] = relationship(secondary=book_subjects)
    locc: Mapped[List["LoCC"]] = relationship(secondary=book_locc)
    summary: Mapped["Summary"] = relationship(back_populates="book")
    embeddings: Mapped["Embedding"] = relationship(back_populates="book")
    cluster: Mapped[int] = mapped_column(ForeignKey("clusters.id"))
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(SQLTypes.String(40))
    birth: Mapped[Optional[datetime.date]] = mapped_column(SQLTypes.Date())
    death: Mapped[Optional[datetime.date]] = mapped_column(SQLTypes.Date())

class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(SQLTypes.String(30), unique=True)

class LoCC(Base):
    __tablename__ = "locc"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(SQLTypes.String(10), unique=True)

from .summaries import Summary
from .embeddings import Embedding
from .cluster import Cluster