from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.worker import celery_app

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/jobs/{task_id}")
async def job_status_ws(websocket: WebSocket, task_id: str):
    """Stream Celery task status/result for a given task_id until completion."""
    await websocket.accept()
    try:
        import asyncio
        while True:
            try:
                result = celery_app.AsyncResult(task_id)
            except RuntimeError as e:
                await websocket.send_json({"task_id": task_id, "status": "UNAVAILABLE", "error": str(e)})
                break
            payload = {"task_id": task_id, "status": result.status}
            if result.ready():
                payload["result"] = result.result if result.successful() else str(result.result)
                await websocket.send_json(payload)
                break
            await websocket.send_json(payload)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
