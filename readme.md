# 🛡️ RoPA 2077 Management Platform

**RoPA 2077** คือระบบจัดการบันทึกรายการประมวลผลข้อมูลส่วนบุคคล (Record of Processing Activities) ที่ออกแบบมาเพื่อให้องค์กรสามารถปฏิบัติตามกฎหมาย PDPA (Personal Data Protection Act) ได้อย่างมีประสิทธิภาพ รองรับทั้งบทบาทผู้ควบคุมข้อมูล (Data Controller) และผู้ประมวลผลข้อมูล (Data Processor)

---

## 🚀 Tech Stack

### Backend (FastAPI)
- **Framework:** FastAPI (Python 3.13)
- **Database ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic V2
- **Database:** PostgreSQL

---

## ✨ Key Features

- **Multi-Role Access Control (RBAC):** แบ่งสิทธิ์การใช้งานชัดเจน (Admin, DPO, Data Owner, Auditor)
- **RoPA Recording:** บันทึกกิจกรรมประมวลผลข้อมูลแยกตามประเภท Controller และ Processor
- **Workflow Approval:** ระบบส่งคำขอให้ DPO ตรวจสอบและอนุมัติรายการ
- **Dynamic Dashboard:** สรุปภาพรวมของกิจกรรมประมวลผลและสถานะ Compliance
- **Data Export/Import:** รองรับการจัดการข้อมูลผ่านไฟล์ CSV/Excel เพื่อความรวดเร็ว
- **Audit Trail:** ระบบตรวจสอบย้อนหลังสำหรับทุกกิจกรรมที่เกิดขึ้น

---

## 📂 Project Structure

```text
.
├── backend/                # FastAPI Application
│   ├── app/
│   │   ├── api/v1/        # API Endpoints (Routing)
│   │   ├── core/          # Configuration & Security
│   │   ├── models/        # SQLAlchemy Models (Database Schema)
│   │   ├── schemas/       # Pydantic Schemas (Data Validation)
│   │   └── main.py        # Entry point
│   ├── tests/             # Pytest / Robot Framework
│   └── requirements.txt
└── docker-compose.yml      # Container Orchestration
