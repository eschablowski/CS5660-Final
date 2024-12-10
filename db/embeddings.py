from .orm_base import Base
from .book import Book
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import sqlalchemy.types as SQLTypes
from sqlalchemy.orm import Mapped
import numpy

class Embedding(Base):
    __tablename__ = "embeddings"
    id: Mapped[int] = mapped_column(primary_key=True)
    embedding_model = mapped_column(SQLTypes.String(10))
    summary: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    title: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    authors: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    subjects: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    locc: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    book: Mapped[Book] = relationship(back_populates="embeddings")

    def __repr__(self) -> str:
        return f"Embedding(id={self.id!r}, model={self.embedding_model!r})"