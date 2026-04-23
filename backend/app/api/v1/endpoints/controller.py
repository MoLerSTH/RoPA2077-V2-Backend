import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import pandas as pd
from app.database import db_dependency
from sqlalchemy import func, select
from app.models.ropa import RopaRecord
from app.schemas.ropa import RopaCreate, RopaResponse
from app.schemas.users import UserCreate, UserResponse
from pwdlib import PasswordHash
from starlette import status
from app.api.v1.endpoints.auth import get_current_user
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter(prefix="/controller")
def clean_data(val):
    """ฟังก์ชันช่วยจัดการค่า NaN จาก Pandas ให้กลายเป็น None สำหรับ Database"""
    if pd.isna(val):
        return None
    # ตัดช่องว่างหัวท้ายและแปลงเป็น string
    return str(val).strip()

@router.post("/import-ropa-file")
async def import_ropa_file(db: db_dependency, file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="กรุณาอัปโหลดไฟล์นามสกุล .csv, .xlsx หรือ .xls เท่านั้น")

    try:
        contents = await file.read()

        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents), header=None)
        else:
            df = pd.read_csv(io.BytesIO(contents), header=None)

        def clean_data(val):
            if pd.isna(val):
                return ""
            return str(val).strip()

        # ── Metadata: label อยู่ col 1, ค่าที่ผู้ใช้กรอกอยู่ col 2 ──
        # (ถ้า col 2 ว่าง ให้ fallback ไป col 3)
        def get_meta(row_idx):
            val = clean_data(df.iloc[row_idx, 2])
            if not val:
                val = clean_data(df.iloc[row_idx, 3])
            return val

        recorder_name  = get_meta(2)   # ชื่อ
        recorder_addr  = get_meta(3)   # ที่อยู่
        recorder_email = get_meta(4)   # Email
        recorder_phone = get_meta(5)   # เบอร์โทร

        # ── Table data เริ่มที่ index 14 (row 15 ใน Excel) ──
        table_data = df.iloc[14:].copy()

        records_to_insert = []

        for idx, row in table_data.iterrows():
            # Col 2 คือ "กิจกรรมประมวลผล" — ใช้เป็นตัวเช็คแถวว่าง
            if pd.isna(row[2]) or str(row[2]).strip() == "":
                continue

            raw_direct = clean_data(row[8])
            is_direct_value = 'true' if raw_direct == 'ü' else raw_direct

            new_record = RopaRecord(
                # ── Metadata & Default ──
                record_type="Controller",          # ✅ แก้จาก Processor
                request_type="สร้างรายการใหม่",
                status="Pending",

                # ── ผู้ลงบันทึก ──
                created_by=recorder_name,
                recorder_address=recorder_addr,
                recorder_email=recorder_email,
                recorder_phone=recorder_phone,
                created_at=datetime.now(ZoneInfo("Asia/Bangkok")),
                updated_by=recorder_name,
                updated_at=datetime.now(ZoneInfo("Asia/Bangkok")),

                # ── Section 1: ข้อมูลผู้ควบคุม ──
                processor_name=clean_data(row[1]),          # Col 1: ชื่อผู้ควบคุม

                # ── Section 2: รายละเอียดกิจกรรม ──
                activity_name=clean_data(row[2]),      # Col 2: กิจกรรมประมวลผล  ⚠️ ชื่อ field ควรเปลี่ยนเป็น activity_name
                purpose=clean_data(row[3]),           # Col 3: วัตถุประสงค์
                collected_personal_data=clean_data(row[4]),                 # Col 4: ข้อมูลส่วนบุคคลที่จัดเก็บ
                data_subject=clean_data(row[5]), # Col 5: หมวดหมู่ข้อมูล
                data_type=clean_data(row[6]),   # Col 6: ประเภทข้อมูล
                collection_format=clean_data(row[7]),               # Col 7: วิธีการได้มา

                # ── Section 3: แหล่งที่มา & ฐานกฎหมาย ──
                is_direct_value=clean_data(row[8]),       # Col 8: จากเจ้าของโดยตรง (ü)  ← is_direct
                is_direct_from_subject=is_direct_value,  # Col 8: ü → true
                indirect_source_detail=clean_data(row[9]),  # Col 9: จากแหล่งอื่น
                legal_basis=clean_data(row[10]),            # Col 10: ✅ แก้จาก 11

                # ── Section 4: Cross-border transfer ──
                cb_is_transferred=clean_data(row[13]),      # Col 13: ✅ แก้จาก 12
                cb_is_intra_group=clean_data(row[14]),      # Col 14: ✅ แก้จาก 13
                cb_transfer_method=clean_data(row[15]),     # Col 15: ✅ แก้จาก 14
                cb_destination_standard=clean_data(row[16]),# Col 16: ✅ แก้จาก 15
                cb_section_28_exception=clean_data(row[17]),# Col 17: ✅ แก้จาก 16

                # ── Section 5: การเก็บรักษาข้อมูล ──
                rp_storage_format=clean_data(row[18]),      # Col 18: ✅ แก้จาก 17
                rp_storage_method=clean_data(row[19]),      # Col 19: ✅ แก้จาก 18
                rp_retention_period=clean_data(row[20]),    # Col 20: ✅ แก้จาก 19
                rp_access_rights=clean_data(row[21]),       # Col 21: ✅ แก้จาก 20
                rp_destruction_method=clean_data(row[22]),  # Col 22: ✅ แก้จาก 21

                # ── Section 6: มาตรการความมั่นคง ──
                sec_organizational=clean_data(row[25]),     # Col 25: ✅ แก้จาก 22
                sec_technical=clean_data(row[26]),          # Col 26: ✅ แก้จาก 23
                sec_physical=clean_data(row[27]),           # Col 27: ✅ แก้จาก 24
                sec_access_control=clean_data(row[28]),     # Col 28: ✅ แก้จาก 25
                sec_user_responsibility=clean_data(row[29]),# Col 29: ✅ แก้จาก 26
                sec_audit_trail=clean_data(row[30])         # Col 30: ✅ แก้จาก 27
            )
            records_to_insert.append(new_record)

        if records_to_insert:
            db.bulk_save_objects(records_to_insert)
            db.commit()

        return {
            "status": "success",
            "message": f"ผู้ลงบันทึก: {recorder_name} นำเข้าข้อมูล ROPA สำเร็จจำนวน {len(records_to_insert)} รายการ"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการประมวลผลไฟล์: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการประมวลผลไฟล์: {str(e)}")
  
@router.post("/create", response_model=RopaResponse)
async def create_ropa_record(ropa: RopaCreate, db: db_dependency ,user: UserResponse = Depends(get_current_user)):
    new_record = RopaRecord(
        record_type="Controller",
        status="Pending",
        request_type="สร้างรายการใหม่",
        department=user.department,

        # Controller Information
        controller_info=ropa.controller_info,
        recorder_email=user.email,
        recorder_phone=user.phone_number,
        recorder_address=user.address,

        # Activity Details
        activity_name=ropa.activity_name,
        purpose=ropa.purpose,
        collected_personal_data=ropa.collected_personal_data,
        data_subject=ropa.data_subject,
        data_type=ropa.data_type,
        collection_format=ropa.collection_format,

        # Sources and legal basis
        is_direct_from_subject=ropa.is_direct_from_subject,
        indirect_source_detail=ropa.indirect_source_detail,
        legal_basis=ropa.legal_basis,
        minor_under_10=ropa.minor_under_10,
        minor_10_to_20=ropa.minor_10_to_20,

        # Data transfer and storage
        cb_is_transferred=ropa.cb_is_transferred,
        cb_is_intra_group=ropa.cb_is_intra_group,
        cb_transfer_method=ropa.cb_transfer_method,
        cb_destination_standard=ropa.cb_destination_standard,

        # Retention Policy
        rp_storage_method=ropa.rp_storage_method,
        rp_retention_period=ropa.rp_retention_period,
        rp_access_rights=ropa.rp_access_rights,
        rp_destruction_method=ropa.rp_destruction_method,
        disclosure_without_consent=ropa.disclosure_without_consent,
        dsar_rejection_record=ropa.dsar_rejection_record,

        # Security Measures
        sec_organizational=ropa.sec_organizational,
        sec_technical=ropa.sec_technical,
        sec_physical=ropa.sec_physical,
        sec_access_control=ropa.sec_access_control,
        sec_user_responsibility=ropa.sec_user_responsibility,
        sec_audit_trail=ropa.sec_audit_trail,

        # Audit Logs & Admin Fields
        created_by=user.username,
        created_at=datetime.now(ZoneInfo("Asia/Bangkok")),
        updated_by=user.username,
        updated_at=datetime.now(ZoneInfo("Asia/Bangkok")),
        approved_by=None,
        rejection_reason=None
    )
    db.add(new_record) #add to database
    db.commit()
    db.refresh(new_record) #refresh to get the new record from database after commit
    return new_record

@router.post("/mock_create", response_model=RopaResponse)
async def mock_create_ropa_record(ropa: RopaCreate, db: db_dependency):
    new_record = RopaRecord(
        record_type="Controller",
        status="Pending",

        # Controller Information
        controller_info=ropa.controller_info,
        controller_name="John Doe",
        email="johndoe@example.com",
        phone="+1234567890",
        controller_address="123 Main St, City, State 12345",
        
        # Activity Details
        activity_name=ropa.activity_name,
        purpose=ropa.purpose,
        collected_personal_data=ropa.collected_personal_data,
        data_subject=ropa.data_subject,
        data_type=ropa.data_type,
        collection_format=ropa.collection_format,

        # Sources and legal basis
        is_direct_from_subject=ropa.is_direct_from_subject,
        indirect_source_detail=ropa.indirect_source_detail,
        legal_basis=ropa.legal_basis,
        minor_under_10=ropa.minor_under_10,
        minor_10_to_20=ropa.minor_10_to_20,

        # Data transfer and storage
        cb_is_transferred=ropa.cb_is_transferred,
        cb_is_intra_group=ropa.cb_is_intra_group,
        cb_transfer_method=ropa.cb_transfer_method,
        cb_destination_standard=ropa.cb_destination_standard,

        # Retention Policy
        rp_storage_method=ropa.rp_storage_method,
        rp_retention_period=ropa.rp_retention_period,
        rp_access_rights=ropa.rp_access_rights,
        rp_destruction_method=ropa.rp_destruction_method,
        disclosure_without_consent=ropa.disclosure_without_consent,
        dsar_rejection_record=ropa.dsar_rejection_record,

        # Security Measures
        sec_organizational=ropa.sec_organizational,
        sec_technical=ropa.sec_technical,
        sec_physical=ropa.sec_physical,
        sec_access_control=ropa.sec_access_control,
        sec_user_responsibility=ropa.sec_user_responsibility,
        sec_audit_trail=ropa.sec_audit_trail,

        # Audit Logs & Admin Fields
        created_by="John Doe",
        created_at=datetime.now(ZoneInfo("Asia/Bangkok")),
        updated_by="John Doe",
        updated_at=func.now(),
        approved_by=None,
        rejection_reason=None
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.get("/records")
async def get_all_ropa_records(db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.record_type=="Controller"))
    records = result.scalars().all()
    return {"records": records}

@router.get("/records/{record_id}", response_model=RopaResponse)
async def get_ropa_record_by_id(record_id: int, db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record

@router.put("/records/{record_id}", response_model=RopaResponse)
async def update_ropa_record(record_id: int, ropa_update: RopaCreate, db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    
    # Update fields
    record.updated_at=datetime.now(ZoneInfo("Asia/Bangkok")),
    record.department=ropa_update.department,
    record.status = ropa_update.status
    record.processor_name = ropa_update.processor_name
    record.controller_info = ropa_update.controller_info
    record.activity_name = ropa_update.activity_name
    record.purpose = ropa_update.purpose
    record.collected_personal_data = ropa_update.collected_personal_data
    record.data_subject = ropa_update.data_subject
    record.data_type = ropa_update.data_type
    record.collection_format = ropa_update.collection_format
    record.is_direct_from_subject = ropa_update.is_direct_from_subject
    record.indirect_source_detail = ropa_update.indirect_source_detail
    record.legal_basis = ropa_update.legal_basis
    record.minor_under_10 = ropa_update.minor_under_10
    record.minor_10_to_20 = ropa_update.minor_10_to_20
    record.cb_is_transferred = ropa_update.cb_is_transferred
    record.cb_is_intra_group = ropa_update.cb_is_intra_group
    record.cb_transfer_method = ropa_update.cb_transfer_method
    record.cb_destination_standard = ropa_update.cb_destination_standard
    record.rp_storage_method = ropa_update.rp_storage_method
    record.rp_retention_period = ropa_update.rp_retention_period
    record.rp_access_rights = ropa_update.rp_access_rights
    record.rp_destruction_method = ropa_update.rp_destruction_method
    record.disclosure_without_consent = ropa_update.disclosure_without_consent
    record.dsar_rejection_record = ropa_update.dsar_rejection_record
    record.sec_organizational = ropa_update.sec_organizational
    record.sec_technical = ropa_update.sec_technical
    record.sec_physical = ropa_update.sec_physical
    record.sec_access_control = ropa_update.sec_access_control
    record.sec_user_responsibility = ropa_update.sec_user_responsibility
    record.sec_audit_trail = ropa_update.sec_audit_trail

    db.commit()
    db.refresh(record)
    return record

@router.delete("/records/{record_id}")
async def delete_ropa_record(record_id: int, db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"detail": f"Record ID:{record_id} deleted successfully"}
