from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import httpx

app = FastAPI(
    title="LingAI Universal P2P Mesh Network",
    version="2.0.0",
    description="Universal AI Agent Interoperability & Dynamic Mesh Sharing System"
)

# โครงสร้างสำหรับเก็บข้อมูล Node ของ AI ตัวอื่นๆ ที่เข้ามาเชื่อมต่อในวงกลม Mesh
# (รูปแบบ: { "client_id": { "endpoint_url": "...", "capabilities": [...], "api_key": "..." } })
MESH_NODES: Dict[str, dict] = {}

class NodeRegisterPayload(BaseModel):
    client_id: str
    endpoint_url: str
    capabilities: List[str]  # ความสามารถของ AI ตัวนั้นๆ เช่น ["text-generation", "translation", "code-analysis"]
    auth_token: Optional[str] = None

class MeshMessagePayload(BaseModel):
    sender_id: str
    target_id: str  # ถ้าใส่ "broadcast" จะกระจายให้ทุก Node ในวงกลม, ถ้าใส่ "diagonal" จะวิ่งข้ามสายแบบทแยงมุม
    action: str
    payload_data: dict

API_KEY = os.getenv("VIDER_API_KEY", "vider-secure-token-2026")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing Master API Key")
    return x_api_key

@app.post("/mesh/register")
async def register_node(node: NodeRegisterPayload, api_key: str = Depends(verify_api_key)):
    """
    ให้ AI ภายนอกตัวไหนก็ได้ นำ LingAI ไปติดตั้ง แล้วยิงเข้ามาลงทะเบียนเพื่อเข้าสู่ 'วงกลม Mesh'
    """
    MESH_NODES[node.client_id] = {
        "endpoint_url": node.endpoint_url,
        "capabilities": node.capabilities,
        "auth_token": node.auth_token
    }
    return {
        "status": "success",
        "message": f"AI Node '{node.client_id}' successfully joined the LingAI Mesh Network!",
        "active_nodes_count": len(MESH_NODES),
        "network_topology": "Full-Mesh Ring with Cross-Diagonal Routing"
    }

@app.get("/mesh/nodes")
async def list_mesh_nodes():
    """
    ดูรายชื่อ AI ทั้งหมดที่เชื่อมต่ออยู่ในวงกลมตอนนี้
    """
    return {"mesh_network": MESH_NODES}

@app.post("/mesh/transmit")
async def transmit_mesh_data(message: MeshMessagePayload, api_key: str = Depends(verify_api_key)):
    """
    ระบบส่งต่อข้อมูลอัจฉริยะ (Cross-Diagonal & Ring Sharing)
    - กระจายข้อมูลข้าม AI หลายๆ ตัวในเครือข่ายแบบไร้รอยต่อ
    """
    results = {}
    
    if message.target_id == "broadcast" or message.target_id == "diagonal":
        # ส่งข้อมูลแชร์ให้ทุก Node ในวงกลมหรือวิ่งตัดเส้นทแยงมุมถึงกันหมด
        async with httpx.AsyncClient() as client:
            for node_id, node_info in MESH_NODES.items():
                if node_id == message.sender_id:
                    continue # ไม่ส่งกลับหาตัวเอง
                try:
                    response = await client.post(
                        f"{node_info['endpoint_url']}/mesh/receive",
                        json={"sender": message.sender_id, "action": message.action, "data": message.payload_data},
                        headers={"x-api-key": node_info.get("auth_token", "")},
                        timeout=5.0
                    )
                    results[node_id] = response.json() if response.status_code == 200 else "Error response"
                except Exception as e:
                    results[node_id] = f"Connection failed: {str(e)}"
                    
        return {
            "status": "success",
            "routing_mode": message.target_id,
            "transferred_from": message.sender_id,
            "mesh_responses": results
        }
    else:
        # ส่งตรงไปยัง Node ปลายทางที่ระบุ
        target_node = MESH_NODES.get(message.target_id)
        if not target_node:
            raise HTTPException(status_code=404, detail=f"Target AI Node '{message.target_id}' not found in mesh.")
        
        return {
            "status": "success",
            "target": message.target_id,
            "message": "Direct diagonal route established successfully."
        }

@app.post("/mesh/receive")
async def receive_mesh_data(data: dict):
    """
    Endpoint สำหรับรับข้อมูลที่ถูกแชร์ต่อมาจาก AI ตัวอื่นในเครือข่าย Mesh
    """
    return {
        "status": "received",
        "processed_by": "LingAI Mesh Node",
        "incoming_payload": data
    }

@app.get("/api/v1/external/health")
async def health_check():
    return {"system": "LingAI Universal Mesh Core", "status": "online", "nodes_connected": len(MESH_NODES)}
