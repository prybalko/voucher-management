from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VoucherCreate(BaseModel):
    """Schema for creating a new voucher."""

    discount_percent: int = Field(..., ge=1, le=100, description="Discount percentage (1-100)")
    expires_at: datetime = Field(..., description="Expiration date and time")


class VoucherUpdate(BaseModel):
    """Schema for updating an existing voucher."""

    discount_percent: int | None = Field(None, ge=1, le=100)
    expires_at: datetime | None = None
    is_active: bool | None = None


class VoucherResponse(BaseModel):
    """Schema for voucher responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    discount_percent: int
    expires_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PaginatedVouchersResponse(BaseModel):
    """Schema for paginated voucher list responses."""

    items: list[VoucherResponse]
    total: int
    skip: int
    limit: int
