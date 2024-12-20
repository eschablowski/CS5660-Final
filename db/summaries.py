
from .orm_base import Base
from .book import Book
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import sqlalchemy.types as SQLTypes
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey

class Summary(Base):
    __tablename__ = "summaries"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(SQLTypes.Integer, ForeignKey("books.id"))
    summarization_model = mapped_column(SQLTypes.String(10))
    summary: Mapped[str] = mapped_column(SQLTypes.String(2048))
    book: Mapped[Book] = relationship(back_populates="summary")
