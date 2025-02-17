
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from typing import List

####


class Base(DeclarativeBase):
    pass

####


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int]          = mapped_column(autoincrement=True, primary_key=True)
    user_id: Mapped[int]     = mapped_column()
    user_link: Mapped[str]   = mapped_column()
