from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
import os

app = FastAPI(title="Chat Vider External Integration API", version="1.0.0")

# กำหนดโครงสร้างข้อมูลที่รับเข้ามาจากภายนอก
class ExternalPayload(BaseModel):
    client_id: str
    action: str
    data: dict

# ระบบตรวจสอบ API Key ง่ายๆ สำหรับความปลอดภัยเบื้องต้น
API_KEY = os.getenv("VIDER_API_KEY", "vider-secure-token-2026")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return x_api_key

@app.post("/api/v1/external/execute")
async def execute_external_task(payload: ExternalPayload, api_key: str = Depends(verify_api_key)):
    """
    Endpoint สำหรับรับคำสั่งหรือข้อมูลจากระบบภายนอกเข้ามาประมวลผลใน Chat Vider
    """
    try:
        # จำลองการทำงานร่วมกันและการประมวลผล
        task_result = {
            "status": "success",
            "message": f"Vider successfully processed action '{payload.action}' from client '{payload.client_id}'",
            "processed_data": payload.data,
            "engine": "Chat Vider Core"
        }
        
        return task_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/external/health")
async def health_check():
    return {"system": "Chat Vider", "status": "online", "integration_ready": True}
