import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
from app.database import db_dependency
from sqlalchemy import func, select
from app.models.ropa import RopaRecord
from app.schemas.ropa import RopaCreate, RopaResponse
from app.schemas.users import UserCreate, UserResponse
from pwdlib import PasswordHash
from starlette import status
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/processor")

def clean_data(val):
    """ฟังก์ชันช่วยจัดการค่า NaN จาก Pandas ให้กลายเป็น None สำหรับ Database"""
    if pd.isna(val):
        return None
    # ตัดช่องว่างหัวท้ายและแปลงเป็น string
    return str(val).strip()

    
@router.post("/import-ropa-file")
async def import_ropa_file(db: db_dependency, file: UploadFile = File(...)):
    # 1. เช็คนามสกุลไฟล์ที่อนุญาต
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="กรุณาอัปโหลดไฟล์นามสกุล .csv, .xlsx หรือ .xls เท่านั้น")

    try:
        contents = await file.read()
        
        # 2. อ่านไฟล์ตามประเภทนามสกุล ให้กลายเป็น DataFrame (df)
        if file.filename.endswith(('.xlsx', '.xls')):
            # ถ้าเป็น Excel ให้อ่านด้วย read_excel
            df = pd.read_excel(io.BytesIO(contents), header=None)
        else:
            # ถ้าเป็น CSV ให้อ่านด้วย read_csv
            df = pd.read_csv(io.BytesIO(contents), header=None)
        
        # 3. ดึงข้อมูลส่วน Metadata ด้านบน (ผู้ลงบันทึก)
        recorder_name = clean_data(df.iloc[1, 2]) if len(df) > 1 else None
        recorder_addr = clean_data(df.iloc[2, 2]) if len(df) > 2 else None
        recorder_email = clean_data(df.iloc[3, 2]) if len(df) > 3 else None
        recorder_phone = clean_data(df.iloc[4, 2]) if len(df) > 4 else None

        # 4. ตัดเอาเฉพาะส่วนที่เป็นตารางข้อมูล (เริ่มที่ Row 15 / Index 14)
        table_data = df.iloc[14:].copy()
        
        records_to_insert = []
        
        # 5. วนลูปและ Map ข้อมูลแต่ละคอลัมน์เข้า Model
        for idx, row in table_data.iterrows():
            # เช็คว่าแถวนี้ไม่มีชื่อกิจกรรมประมวลผล (Col 3) ให้ข้ามไปเลย ถือเป็นบรรทัดว่าง
            if pd.isna(row[3]) or str(row[3]).strip() == "":
                continue
            
            # จัดการเงื่อนไข is_direct_from_controller
            raw_direct_controller = clean_data(row[9])
            if raw_direct_controller == 'ü':
                is_direct_value = 'true'
            else:
                is_direct_value = raw_direct_controller
                
            new_record = RopaRecord(
                # --- Metadata & Default Fields ---
                record_type="Processor",
                request_type="สร้างรายการใหม่",
                status="Pending",
                
                # --- ข้อมูลผู้ลงบันทึก ---
                created_by=recorder_name,
                recorder_address=recorder_addr,
                recorder_email=recorder_email,
                recorder_phone=recorder_phone,

                # --- Section 1: ข้อมูลผู้ควบคุม/ผู้ประมวลผล ---
                processor_name=clean_data(row[1]),
                controller_address=clean_data(row[2]),
                
                # --- Section 2: รายละเอียดกิจกรรมประมวลผล ---
                activity_name=clean_data(row[3]),
                purpose=clean_data(row[4]),
                collected_personal_data=clean_data(row[5]),
                data_subject=clean_data(row[6]),
                data_type=clean_data(row[7]),
                collection_format=clean_data(row[8]),
                
                # --- Section 3: แหล่งที่มา และ ฐานกฎหมาย ---
                is_direct_from_controller=is_direct_value,
                indirect_source_detail=clean_data(row[10]),
                legal_basis=clean_data(row[11]),
                
                # --- Section 4: การส่งข้อมูลต่างประเทศ และ นโยบายการจัดเก็บ ---
                cb_is_transferred=clean_data(row[12]),
                cb_is_intra_group=clean_data(row[13]),
                cb_transfer_method=clean_data(row[14]),
                cb_destination_standard=clean_data(row[15]),
                disclosure_without_consent=clean_data(row[16]),
                
                rp_storage_method=clean_data(row[18]),
                rp_retention_period=clean_data(row[19]),
                rp_access_rights=clean_data(row[20]),
                rp_destruction_method=clean_data(row[21]),
                
                # --- Section 5: มาตรการความมั่นคงปลอดภัย ---
                sec_organizational=clean_data(row[22]),
                sec_technical=clean_data(row[23]),
                sec_physical=clean_data(row[24]),
                sec_access_control=clean_data(row[25]),
                sec_user_responsibility=clean_data(row[26]),
                sec_audit_trail=clean_data(row[27])
            )
            records_to_insert.append(new_record)

        # 6. บันทึกลง Database
        if records_to_insert:
            db.bulk_save_objects(records_to_insert)
            db.commit()

        return {
            "status": "success", 
            "message": f"ดึงข้อมูลผู้ลงบันทึก: {recorder_name} และนำเข้าข้อมูล ROPA สำเร็จจำนวน {len(records_to_insert)} รายการ (จากไฟล์ {file.filename})"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการประมวลผลไฟล์: {str(e)}")
    
@router.post("/create", response_model=RopaResponse)
async def create_ropa_record(ropa: RopaCreate, db: db_dependency ,user: UserResponse = Depends(get_current_user)):
    new_record = RopaRecord(
        record_type = "Processor",
        status = "Pending",
        request_type = "สร้างรายการใหม่",
        department=user.department,
        processor_name=ropa.processor_name,
        controller_address=ropa.controller_address,
        # Processor Information
        controller_info = ropa.controller_info,
        recorder_email = user.email,
        recorder_phone = user.phone_number,
        recorder_address = user.address,

        # Activity Details
        activity_name = ropa.activity_name,
        purpose = ropa.purpose,
        collected_personal_data = ropa.collected_personal_data,
        data_subject = ropa.data_subject,
        data_type = ropa.data_type,
        collection_format = ropa.collection_format,

        # Sources and legal basis
        is_direct_from_subject = ropa.is_direct_from_subject,
        indirect_source_detail = ropa.indirect_source_detail,
        legal_basis = ropa.legal_basis,
        minor_under_10 = ropa.minor_under_10,
        minor_10_to_20 = ropa.minor_10_to_20,

        # Data transfer and storage
        cb_is_transferred = ropa.cb_is_transferred,
        cb_is_intra_group = ropa.cb_is_intra_group,
        cb_transfer_method = ropa.cb_transfer_method,
        cb_destination_standard = ropa.cb_destination_standard,

        # Retention Policy
        rp_storage_method = ropa.rp_storage_method,
        rp_retention_period = ropa.rp_retention_period,
        rp_access_rights = ropa.rp_access_rights,
        rp_destruction_method = ropa.rp_destruction_method,
        disclosure_without_consent = ropa.disclosure_without_consent,
        dsar_rejection_record = ropa.dsar_rejection_record,

        # Security Measures
        sec_organizational = ropa.sec_organizational,
        sec_technical = ropa.sec_technical,
        sec_physical = ropa.sec_physical,
        sec_access_control = ropa.sec_access_control,
        sec_user_responsibility = ropa.sec_user_responsibility,
        sec_audit_trail = ropa.sec_audit_trail,

        # Audit Fields and Admin Fields
        created_by = user.username,
        created_at = func.current_timestamp(),
        updated_by = user.username,
        updated_at = func.current_timestamp(),
        approved_by = None,
        rejection_reason = None
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.get("/records")
async def get_all_ropa_records(db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.record_type == "Processor"))
    records = result.scalars().all()
    return {"records": records }

@router.get("/records/{record_id}", response_model=RopaResponse)
async def get_ropa_record_by_id(record_id: int, db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record

@router.put("/records/{record_id}", response_model=RopaResponse)
async def update_ropa_record(record_id: int, ropa: RopaCreate, db: db_dependency, user: UserResponse = Depends(get_current_user)):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    record.status=ropa.status
    record.controller_info = ropa.controller_info
    record.recorder_email = user.email
    record.recorder_phone = user.phone_number
    record.recorder_address = user.address
    record.activity_name = ropa.activity_name
    record.purpose = ropa.purpose
    record.collected_personal_data = ropa.collected_personal_data
    record.data_subject = ropa.data_subject
    record.data_type = ropa.data_type
    record.collection_format = ropa.collection_format
    record.is_direct_from_subject = ropa.is_direct_from_subject
    record.indirect_source_detail = ropa.indirect_source_detail
    record.legal_basis = ropa.legal_basis
    record.minor_under_10 = ropa.minor_under_10
    record.minor_10_to_20 = ropa.minor_10_to_20
    record.cb_is_transferred = ropa.cb_is_transferred
    record.cb_is_intra_group = ropa.cb_is_intra_group
    record.cb_transfer_method = ropa.cb_transfer_method
    record.cb_destination_standard = ropa.cb_destination_standard
    record.rp_storage_method = ropa.rp_storage_method
    record.rp_retention_period = ropa.rp_retention_period
    record.rp_access_rights = ropa.rp_access_rights
    record.rp_destruction_method = ropa.rp_destruction_method
    record.disclosure_without_consent = ropa.disclosure_without_consent
    record.dsar_rejection_record = ropa.dsar_rejection_record
    record.sec_organizational = ropa.sec_organizational
    record.sec_technical = ropa.sec_technical
    record.sec_physical = ropa.sec_physical
    record.sec_access_control = ropa.sec_access_control
    record.sec_user_responsibility = ropa.sec_user_responsibility
    record.sec_audit_trail = ropa.sec_audit_trail
    record.updated_by = user.username
    record.updated_at = func.current_timestamp()
    record.approved_by = None
    record.rejection_reason = None


    db.commit()
    db.refresh(record)
    return record

@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ropa_record(record_id: int, db: db_dependency):
    result = db.execute(select(RopaRecord).where(RopaRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    db.delete(record)
    db.commit()