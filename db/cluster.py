from .orm_base import Base
from typing import List
from .book import Book
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import sqlalchemy.types as SQLTypes
from sqlalchemy.orm import Mapped
import numpy

class Cluster(Base):
    __tablename__ = "clusters"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    centroid: Mapped[numpy.array] = mapped_column(SQLTypes.PickleType)
    books: Mapped[List[Book]] = relationship()

    def __repr__(self) -> str:
        return f"Cluster(id={self.id!r})"