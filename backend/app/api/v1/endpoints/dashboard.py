from fastapi import APIRouter, HTTPException
from app.database import db_dependency
from sqlalchemy import select, func, case
from app.models.ropa import RopaRecord
from starlette import status

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(db: db_dependency):
    total_records = db.query(RopaRecord).count()
    pending_records = db.query(RopaRecord).filter(RopaRecord.status == "Pending").count()
    approved_records = db.query(RopaRecord).filter(RopaRecord.status == "Approved").count()
    rejected_records = db.query(RopaRecord).filter(RopaRecord.status == "Rejected").count()

    dept_query = db.query(
        RopaRecord.department,
        func.count(RopaRecord.id).label("total"),
        # นับเฉพาะสถานะ Approved
        func.count(case((RopaRecord.status == 'Approved', RopaRecord.id))).label("approved_count"),
        # นับเฉพาะสถานะ Rejected
        func.count(case((RopaRecord.status == 'Rejected', RopaRecord.id))).label("rejected_count"),
        # นับเฉพาะสถานะ Pending
        func.count(case((RopaRecord.status == 'Pending', RopaRecord.id))).label("pending_count")
    ).group_by(RopaRecord.department).all()
    dept_data = [
        {
            "name": dept if dept else "ไม่ระบุแผนก",
            "count": total,
            "Approved": approved,
            "Rejected": rejected,
            "Pending": pending
        }
        for dept, total, approved, rejected, pending in dept_query
    ]

    # 3. นับจำนวนตามฐานกฎหมาย (Legal Basis)
    legal_query = db.query(RopaRecord.legal_basis, func.count(RopaRecord.id)).group_by(RopaRecord.legal_basis).all()
    legal_data = [{"name": basis, "count": count} for basis, count in legal_query if basis]

    # ทำแบบเดียวกันกับ Data Types และ Trends...

    return {
        "statCards": {
            "total": total_records,
            "pending": pending_records,
            "approved": approved_records,
            "rejected": rejected_records
        },
        "deptData": dept_data,
        "legalData": legal_data,
        # ส่งข้อมูลอื่นๆ ที่ aggregate แล้วกลับไป
    }