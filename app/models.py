import secrets
import string
from datetime import UTC, datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def generate_voucher_code(length: int = 8) -> str:
    """Generate a random alphanumeric voucher code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def utc_now() -> datetime:
    return datetime.now(UTC)


class Voucher(Base):
    __tablename__ = "vouchers"
    __table_args__ = (
        CheckConstraint(
            "discount_percent >= 1 AND discount_percent <= 100",
            name="check_discount_percent_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(
        String(12), unique=True, index=True, default=generate_voucher_code
    )
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
