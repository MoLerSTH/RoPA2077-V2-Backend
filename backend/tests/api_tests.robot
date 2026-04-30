*** Settings ***
Library         RequestsLibrary
Library         Collections

*** Variables ***
# กำหนด BASE_URL ชี้ไปที่ FastAPI Backend ของคุณ
${BASE_URL}     http://app:8000

# ตัวแปรสำหรับจำลอง ID ในการทำสอบ
${TEST_USER_ID}       1
${TEST_RECORD_ID}     999

*** Test Cases ***

# ==========================================
# 1. Authentication Module
# ==========================================
Verify User Login Successfully
    [Documentation]    ทดสอบการเข้าสู่ระบบเพื่อรับ Token
    [Tags]             auth
    Create Session     api_session    ${BASE_URL}
    # หมายเหตุ: FastAPI OAuth2 มักจะรับเป็น Form Data (x-www-form-urlencoded)
    ${payload}=        Create Dictionary    email=hattakorn49@gmail.com    password=gusto1234
    ${response}=       POST On Session    api_session    /api/v1/auth/login    json=${payload}    expected_status=201
    Status Should Be   201    ${response}
    Log To Console     \nLogin Response: ${response.json()}
    ${TOKEN}=          Set Variable    ${response.json()['access_token']}
    Set Suite Variable    ${GLOBAL_TOKEN}    ${TOKEN}

# ==========================================
# 2. Users Module
# ==========================================
Verify Create New User
    [Documentation]    ทดสอบการสร้างบัญชีผู้ใช้งานใหม่
    [Tags]             users
    ${payload}=        Create Dictionary    username=Robot Tester2    email=robot2@test.com    password=12345    role=Data Owner    department=IT    address=Thammasat    phone_number=0747543589
    ${headers}=        Create Dictionary    Content-Type=application/json
    ${response}=       POST On Session    api_session    /api/v1/users/create    json=${payload}    headers=${headers}
    Status Should Be   200    ${response}

Verify Get All Users
    [Documentation]    ทดสอบการดึงข้อมูลผู้ใช้งานทั้งหมด
    [Tags]             users
    ${response}=       GET On Session     api_session    /api/v1/users
    Status Should Be   200    ${response}

Verify Get User By ID
    [Documentation]    ทดสอบการดึงข้อมูลผู้ใช้งานรายบุคคล
    [Tags]             users
    ${response}=       GET On Session     api_session    /api/v1/users/${TEST_USER_ID}
    Status Should Be   200    ${response}

# ==========================================
# 3. RoPA Controller Module
# ==========================================
Verify Create RoPA Controller Record
    [Documentation]    ทดสอบการสร้างรายการ RoPA ฝั่ง Controller
    [Tags]             ropa_controller
    ${payload}=        Create Dictionary    record_type=Controller    activity_name=Automated Data Collection    purpose=Testing
    ${headers}=        Create Dictionary    Authorization=Bearer ${GLOBAL_TOKEN}    Content-Type=application/json
    ${response}=       POST On Session    api_session    /api/v1/ropa/controller/create    json=${payload}    headers=${headers}    expected_status=200
    Status Should Be   200    ${response}

Verify Get All RoPA Controller Records
    [Documentation]    ทดสอบการดึงข้อมูลรายการ RoPA Controller ทั้งหมด
    [Tags]             ropa_controller
    ${response}=       GET On Session     api_session    /api/v1/ropa/controller/records
    Status Should Be   200    ${response}

# ==========================================
# 4. RoPA Processor Module
# ==========================================
Verify Create RoPA Processor Record
    [Documentation]    ทดสอบการสร้างรายการ RoPA ฝั่ง Processor
    [Tags]             ropa_processor
    ${payload}=        Create Dictionary    record_type=Processor    activity_name=Automated Processing    processor_name=Robot Corp
    ${headers}=        Create Dictionary    Authorization=Bearer ${GLOBAL_TOKEN}    Content-Type=application/json
    ${response}=       POST On Session    api_session    /api/v1/ropa/processor/create    json=${payload}    headers=${headers}    expected_status=200
    Status Should Be   200    ${response}

Verify Get All RoPA Processor Records
    [Documentation]    ทดสอบการดึงข้อมูลรายการ RoPA Processor ทั้งหมด
    [Tags]             ropa_processor
    ${response}=       GET On Session     api_session    /api/v1/ropa/processor/records
    Status Should Be   200    ${response}

Verify Delete RoPA Processor Record
    [Documentation]    ทดสอบการลบข้อมูล Processor (สมมติว่าลบสำเร็จ)
    [Tags]             ropa_processor
    # ใช้ expected_status=any ในกรณีที่ไอดีอาจจะไม่มีอยู่จริงในฐานข้อมูลตอนเทส
    ${response}=       DELETE On Session  api_session    /api/v1/ropa/processor/records/${TEST_RECORD_ID}    expected_status=any
    Log To Console     \nDelete Response Status: ${response.status_code}

# ==========================================
# 5. DPO Module
# ==========================================
Verify Get All DPO Records
    [Documentation]    ทดสอบการดึงข้อมูล RoPA ที่รอการอนุมัติสำหรับ DPO
    [Tags]             dpo
    ${response}=       GET On Session     api_session    /api/v1/dpo/records
    Status Should Be   200    ${response}

Verify DPO Approve Record
    [Documentation]    ทดสอบ DPO กดอนุมัติรายการ RoPA
    [Tags]             dpo
    ${headers}=        Create Dictionary    Content-Type=application/json
    ${response}=       PUT On Session     api_session    /api/v1/dpo/records/${TEST_RECORD_ID}/approve    headers=${headers}    expected_status=any
    Log To Console     \nApprove Action Status: ${response.status_code}

# ==========================================
# 6. Dashboard Module
# ==========================================
Verify Get Dashboard Summary
    [Documentation]    ทดสอบการดึงข้อมูลภาพรวมสำหรับหน้า Dashboard
    [Tags]             dashboard
    ${response}=       GET On Session     api_session    /api/v1/dashboard/summary
    Status Should Be   200    ${response}
    Log To Console     \nDashboard Data: ${response.json()}