from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# 1. Base Schema (รวมแอตทริบิวต์หลักทั้งหมด)
class RopaBase(BaseModel):
    record_type: Optional[str] = None
    request_type: Optional[str] = None
    department: Optional[str] = None
    activity_name: Optional[str] = None
    purpose: Optional[str] = None
    data_subject: Optional[str] = None
    collected_personal_data: Optional[str] = None
    collected_data: Optional[str] = None
    legal_basis: Optional[str] = None
    status: Optional[str] = None
    controller_info: Optional[str] = None
    processor_name: Optional[str] = None
    controller_address: Optional[str] = None
    data_type: Optional[str] = None
    collection_format: Optional[str] = None
    is_direct_from_subject: Optional[str] = None
    is_direct_from_controller: Optional[str] = None
    indirect_source_detail: Optional[str] = None
    minor_under_10: Optional[str] = None
    minor_10_to_20: Optional[str] = None
    cb_is_transferred: Optional[str] = None
    cb_is_intra_group: Optional[str] = None
    cb_transfer_method: Optional[str] = None
    cb_destination_standard: Optional[str] = None
    cb_section_28_exception: Optional[str] = None
    rp_storage_format: Optional[str] = None
    rp_storage_method: Optional[str] = None
    rp_retention_period: Optional[str] = None
    rp_access_rights: Optional[str] = None
    rp_destruction_method: Optional[str] = None
    disclosure_without_consent: Optional[str] = None
    dsar_rejection_record: Optional[str] = None
    sec_organizational: Optional[str] = None
    sec_technical: Optional[str] = None
    sec_physical: Optional[str] = None
    sec_access_control: Optional[str] = None
    sec_user_responsibility: Optional[str] = None
    sec_audit_trail: Optional[str] = None
    rejection_reason: Optional[str] = None
    recorder_email: Optional[str] = None
    recorder_phone: Optional[str] = None
    recorder_address: Optional[str] = None

# 2. Schema สำหรับการ Create (รับข้อมูลมาจาก Frontend ตอนบันทึก)
class RopaCreate(RopaBase):
    record_type: str 
    activity_name: str


# 3. Schema สำหรับการ Update (การแก้ไขข้อมูลกิจกรรมประมวลผล)
class RopaUpdate(RopaBase):
    pass

# 4. Schema สำหรับการ Response (ส่งข้อมูลกลับไปที่ Frontend NextJS)
class RopaResponse(RopaBase):
    id: int
    activity_name: str
    purpose: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    approved_by: Optional[str] = None
    submitted_date: Optional[datetime] = None

    # สำคัญมากสำหรับ SQLAlchemy 2.0 + Pydantic v2
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)