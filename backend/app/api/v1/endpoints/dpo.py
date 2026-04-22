# app/api/v1/dpo.py
from fastapi import APIRouter, HTTPException
from app.database import db_dependency
from sqlalchemy import select
from app.models.ropa import RopaRecord
from starlette import status

router = APIRouter()

@router.get("/records", status_code=status.HTTP_200_OK)
async def get_records(db: db_dependency):
    result = db.execute(select(RopaRecord))
    records = result.scalars().all()
    if not records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No records found")
    return records

@router.get("/records/{record_id}", status_code=status.HTTP_200_OK)
async def get_record_by_id(record_id: int, db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record

# rejection
@router.put("/records/{record_id}/reject", status_code=status.HTTP_200_OK)
async def reject_record(record_id: int, db: db_dependency, rejection_reason: str = None):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    record.status = "Rejected"
    record.rejection_reason = rejection_reason
    db.commit()
    db.refresh(record)
    return {"message": "Record rejected successfully", 
            "record id": record_id, 
            "status": record.status,
            "rejection reason": rejection_reason}

# approval
@router.put("/records/{record_id}/approve", status_code=status.HTTP_200_OK)
async def approve_record(record_id: int, db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    record.status = "Approved"
    db.commit()
    db.refresh(record)
    return {"message": "Record approved successfully", 
            "record id": record_id,
            "status": record.status}