from sqlalchemy import Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.globals import USER_ROLE_SELLER, USER_ROLE_BUYER


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True,
                                       nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # "buyer" or "seller or admin"
    role: Mapped[str] = mapped_column(String, default=USER_ROLE_BUYER)

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates=USER_ROLE_SELLER
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user"
    )
