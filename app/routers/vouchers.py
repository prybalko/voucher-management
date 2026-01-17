from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Query as SQLAlchemyQuery
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Voucher
from app.schemas import (
    PaginatedVouchersResponse,
    VoucherCreate,
    VoucherResponse,
    VoucherUpdate,
)

router = APIRouter(prefix="/vouchers", tags=["vouchers"])


def _active_vouchers_query(db: Session) -> SQLAlchemyQuery[Voucher]:
    """Base query for active, non-expired vouchers."""
    now = datetime.now(UTC)
    return db.query(Voucher).filter(Voucher.is_active.is_(True), Voucher.expires_at > now)


@router.post("/", response_model=VoucherResponse, status_code=status.HTTP_201_CREATED)
def create_voucher(voucher_in: VoucherCreate, db: Session = Depends(get_db)) -> Voucher:
    """Create a new voucher with an auto-generated code."""
    voucher = Voucher(
        discount_percent=voucher_in.discount_percent,
        expires_at=voucher_in.expires_at,
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher


@router.get("/", response_model=PaginatedVouchersResponse)
def list_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
) -> dict:
    """List active, non-expired vouchers with pagination."""
    base_query = _active_vouchers_query(db)
    total = base_query.with_entities(func.count(Voucher.id)).scalar()
    vouchers = (
        base_query.order_by(Voucher.created_at.desc(), Voucher.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "items": vouchers,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{code}", response_model=VoucherResponse)
def get_voucher(code: str, db: Session = Depends(get_db)) -> Voucher:
    """Retrieve an active, non-expired voucher by its code."""
    voucher = _active_vouchers_query(db).filter(Voucher.code == code).first()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voucher with code '{code}' not found",
        )
    return voucher


@router.patch("/{code}", response_model=VoucherResponse)
def update_voucher(code: str, voucher_in: VoucherUpdate, db: Session = Depends(get_db)) -> Voucher:
    """Update an existing voucher with pessimistic locking."""
    voucher = db.query(Voucher).filter(Voucher.code == code).with_for_update().first()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voucher with code '{code}' not found",
        )

    update_data = voucher_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voucher, field, value)

    db.commit()
    db.refresh(voucher)
    return voucher


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_voucher(code: str, db: Session = Depends(get_db)) -> None:
    """Deactivate a voucher (soft delete) with pessimistic locking."""
    voucher = db.query(Voucher).filter(Voucher.code == code).with_for_update().first()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voucher with code '{code}' not found",
        )

    voucher.is_active = False
    db.commit()
