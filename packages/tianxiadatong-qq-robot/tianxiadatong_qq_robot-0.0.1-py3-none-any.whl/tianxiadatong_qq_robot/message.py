import json

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from tianxiadatong_qq_robot import processor

router = APIRouter(prefix="/message")

#此API端点为接收机器人信息而设计
@router.post("/recv")
async def recv_message(request: Request):
    try:
        data = await request.json()
        await processor.covertMessageAndSend(data)
        return {"status": "ok"}
    except UnicodeDecodeError as e:
        return JSONResponse(status_code=400, content={"error": f"Unicode decode error: {str(e)}"})
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid JSON: {str(e)}"})

