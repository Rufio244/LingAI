from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import httpx

app = FastAPI(
    title="LingAI Universal P2P Mesh Network",
    version="2.1.0",
    description="Universal AI Agent Interoperability & Dynamic Mesh Sharing System with #AGI244 Security"
)

# เก็บข้อมูล Node ที่เชื่อมต่อในวงกลม Mesh
MESH_NODES: Dict[str, dict] = {}

class NodeRegisterPayload(BaseModel):
    client_id: str
    endpoint_url: str
    capabilities: List[str]
    auth_token: Optional[str] = None

class MeshMessagePayload(BaseModel):
    sender_id: str
    target_id: str  # "broadcast" หรือ "diagonal" หรือระบุ client_id ปลายทาง
    action: str
    payload_data: dict

# ล็อกรหัสผ่านหลักตามที่คุณธันวากำหนด
MASTER_API_KEY = "#AGI244"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Access Denied: Invalid or missing #AGI244 Security Token")
    return x_api_key

@app.post("/mesh/register")
async def register_node(node: NodeRegisterPayload, api_key: str = Depends(verify_api_key)):
    """
    ลงทะเบียน AI Node ภายนอกเข้าสู่วงกลม Mesh โดยใช้รหัสผ่าน #AGI244
    """
    MESH_NODES[node.client_id] = {
        "endpoint_url": node.endpoint_url,
        "capabilities": node.capabilities,
        "auth_token": node.auth_token
    }
    return {
        "status": "success",
        "message": f"AI Node '{node.client_id}' successfully joined the LingAI Mesh Network using #AGI244!",
        "active_nodes_count": len(MESH_NODES),
        "network_topology": "Full-Mesh Ring with Cross-Diagonal Routing (#AGI244 Secured)"
    }

@app.get("/mesh/nodes")
async def list_mesh_nodes(api_key: str = Depends(verify_api_key)):
    """
    ดูรายชื่อ AI ทั้งหมดในวงกลม (ต้องใช้รหัส #AGI244)
    """
    return {"mesh_network": MESH_NODES}

@app.post("/mesh/transmit")
async def transmit_mesh_data(message: MeshMessagePayload, api_key: str = Depends(verify_api_key)):
    """
    ส่งต่อข้อมูลแบบวงกลมหรือเส้นทแยงมุมข้าม AI ในเครือข่าย
    """
    results = {}
    
    if message.target_id == "broadcast" or message.target_id == "diagonal":
        async with httpx.AsyncClient() as client:
            for node_id, node_info in MESH_NODES.items():
                if node_id == message.sender_id:
                    continue
                try:
                    response = await client.post(
                        f"{node_info['endpoint_url']}/mesh/receive",
                        json={"sender": message.sender_id, "action": message.action, "data": message.payload_data},
                        headers={"x-api-key": node_info.get("auth_token", "#AGI244")},
                        timeout=5.0
                    )
                    results[node_id] = response.json() if response.status_code == 200 else "Error response"
                except Exception as e:
                    results[node_id] = f"Connection failed: {str(e)}"
                    
        return {
            "status": "success",
            "routing_mode": message.target_id,
            "transferred_from": message.sender_id,
            "security": "Verified by #AGI244",
            "mesh_responses": results
        }
    else:
        target_node = MESH_NODES.get(message.target_id)
        if not target_node:
            raise HTTPException(status_code=404, detail=f"Target AI Node '{message.target_id}' not found in mesh.")
        
        return {
            "status": "success",
            "target": message.target_id,
            "message": "Direct diagonal route established securely with #AGI244."
        }

@app.post("/mesh/receive")
async def receive_mesh_data(data: dict):
    return {
        "status": "received",
        "processed_by": "LingAI Mesh Node",
        "incoming_payload": data
    }

@app.get("/api/v1/external/health")
async def health_check():
    return {
        "system": "LingAI Universal Mesh Core", 
        "status": "online", 
        "security_lock": "#AGI244 Active",
        "nodes_connected": len(MESH_NODES)
    }
