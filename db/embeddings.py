from .orm_base import Base
from .book import Book
from .summaries import Summary
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import sqlalchemy.types as SQLTypes
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
import numpy

class Embedding(Base):
    __tablename__ = "embeddings"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(SQLTypes.Integer, ForeignKey("books.id"))
    summary_id: Mapped[int] = mapped_column(SQLTypes.Integer, ForeignKey("summaries.id"))
    embedding_model = mapped_column(SQLTypes.String(10))
    summary: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    title: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    authors: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    subjects: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    locc: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    book: Mapped[Book] = relationship(back_populates="embeddings")
    summary: Mapped[Summary] = relationship()
    combined: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)

    def __repr__(self) -> str:
        return f"Embedding(id={self.id!r}, model={self.embedding_model!r})"