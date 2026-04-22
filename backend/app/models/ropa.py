from sqlalchemy import Column, String, Integer, Text, DateTime, func
from app.database import Base

class RopaRecord(Base):
    __tablename__ = "ropa_records"

    # 1. Primary & Core Metadata
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # รหัสรายการ (Cxxx/Pxxx)
    record_type = Column(String(50), index=True)          # ประเภทเมนู (Controller / Processor)
    request_type = Column(String(50))                    # ประเภทคำขอ (สร้างรายการใหม่ / แก้ไข / ลบรายการ)
    department = Column(String(50))
    status = Column(String(50), default="Pending")       # สถานะ (Approved / Pending / Rejected)
    
    # 2. ข้อมูลผู้ควบคุมและผู้ลงบันทึก (Section 1)
    controller_info = Column(Text, nullable=True)        # ข้อมูลเกี่ยวกับผู้ควบคุมข้อมูลส่วนบุคคล (Controller)
    controller_name = Column(String(255), nullable=True) # ชื่อผู้ควบคุมข้อมูลส่วนบุคคล (Controller)
    processor_name = Column(String(255), nullable=True)  # ชื่อผู้ประมวลผลข้อมูลส่วนบุคคล (Processor)
    controller_address = Column(Text, nullable=True)     # ที่อยู่ผู้ควบคุมข้อมูลส่วนบุคคล

    # 3. รายละเอียดกิจกรรมประมวลผล (Section 2)
    activity_name = Column(String(255), index=True)      # กิจกรรมประมวลผล (Activity Name)
    purpose = Column(Text)                               # วัตถุประสงค์ของการประมวลผล (Purpose)
    data_subject = Column(String(255))          # หมวดหมู่ของข้อมูล/เจ้าของข้อมูล (Data Subject)
    collected_personal_data = Column(Text)               # ข้อมูลส่วนบุคคลที่จัดเก็บ
    data_type = Column(String(255))                      # ประเภทของข้อมูล (ทั่วไป / อ่อนไหว)
    collection_format = Column(String(255))              # วิธีการได้มาซึ่งข้อมูล (Soft File / Hard Copy)

    # 4. แหล่งที่มา และ ฐานกฎหมาย (Section 3)
    is_direct_from_subject = Column(String(50))          # รับจากเจ้าของข้อมูลโดยตรงหรือไม่ (Controller)
    is_direct_from_controller = Column(String(50))       # รับจากผู้ควบคุมโดยตรงหรือไม่ (Processor)
    indirect_source_detail = Column(Text, nullable=True) # กรณีแหล่งอื่น (ระบุแหล่งที่มา)
    legal_basis = Column(String(255))                    # ฐานในการประมวลผล (Legal Basis)
    minor_under_10 = Column(String(255), nullable=True)  # การขอความยินยอมผู้เยาว์ (อายุไม่เกิน 10 ปี)
    minor_10_to_20 = Column(String(255), nullable=True)  # การขอความยินยอมผู้เยาว์ (อายุ 10 - 20 ปี)

    # 5. การส่งข้อมูลต่างประเทศ และ นโยบายการจัดเก็บ (Section 4)
    cb_is_transferred = Column(String(50))               # ส่งหรือโอนไปต่างประเทศ?
    cb_is_intra_group = Column(String(50))               # ส่งให้บริษัทในเครือต่างประเทศ?
    cb_transfer_method = Column(String(255), nullable=True)      # วิธีการโอนข้อมูล
    cb_destination_standard = Column(String(255), nullable=True) # มาตรฐานประเทศปลายทาง
    
    rp_storage_method = Column(String(255), nullable=True)       # วิธีการเก็บรักษาข้อมูล
    rp_retention_period = Column(String(255), nullable=True)     # ระยะเวลาเก็บรักษา
    rp_access_rights = Column(String(255), nullable=True)        # สิทธิ/วิธีการเข้าถึงข้อมูล
    rp_destruction_method = Column(String(255), nullable=True)    # วิธีทำลายข้อมูลเมื่อสิ้นสุด
    
    disclosure_without_consent = Column(Text, nullable=True)     # การเปิดเผยข้อมูลที่ได้รับยกเว้นไม่ต้องขอความยินยอม
    dsar_rejection_record = Column(Text, nullable=True)          # การปฏิเสธคำขอการใช้สิทธิ (DSAR Rejection)

    # 6. มาตรการความมั่นคงปลอดภัย (Section 5)
    sec_organizational = Column(Text, nullable=True)      # มาตรการเชิงองค์กร
    sec_technical = Column(Text, nullable=True)           # มาตรการเชิงเทคนิค
    sec_physical = Column(Text, nullable=True)            # มาตรการทางกายภาพ
    sec_access_control = Column(Text, nullable=True)      # การควบคุมการเข้าถึงข้อมูล
    sec_user_responsibility = Column(Text, nullable=True) # การกำหนดหน้าที่ผู้ใช้งาน
    sec_audit_trail = Column(Text, nullable=True)         # มาตรการตรวจสอบย้อนหลัง

    # 7. Audit Log & Admin Fields
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # วันที่สร้างรายการ
    created_by = Column(String(255))                                        # สร้างโดย
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())       # แก้ไขล่าสุดเมื่อ
    updated_by = Column(String(255))                                        # แก้ไขล่าสุดโดย
    approved_by = Column(String(255), nullable=True)                        # ผู้อนุมัติ (DPO)
    rejection_reason = Column(Text, nullable=True)                          # หมายเหตุจาก DPO (กรณี Rejected)
    recorder_email = Column(String(255), nullable=True)                     # อีเมลผู้ลงบันทึก (สำหรับส่งแจ้งเตือน)
    recorder_phone = Column(String(20), nullable=True)                      # เบอร์โทรศัพท์ผู้ลงบันทึก (สำหรับส่งแจ้งเตือน)
    recorder_address = Column(Text, nullable=True)                          # ที่อยู่ผู้ลงบันทึก (สำหรับส่งแจ้งเตือน)
    