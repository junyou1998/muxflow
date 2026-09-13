from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.queue_manager import queue_manager, QueueStatus

router = APIRouter(prefix="/api/mux", tags=["mux"])

class AddJobsRequest(BaseModel):
    jobs: List[Dict[str, Any]]

class StartQueueRequest(BaseModel):
    jobs: Optional[List[Dict[str, Any]]] = None
    abort_on_error: Optional[bool] = False

@router.post("/queue/add")
async def add_jobs_to_queue(req: AddJobsRequest):
    if not req.jobs:
        raise HTTPException(status_code=400, detail="No jobs provided")
    return queue_manager.add_jobs(req.jobs)

@router.delete("/queue/{job_idx}")
async def remove_job_from_queue(job_idx: int):
    return queue_manager.remove_job(job_idx)

@router.post("/start")
async def start_muxing(req: StartQueueRequest):
    if req.jobs:
        queue_manager.add_jobs(req.jobs)
    if queue_manager.status == QueueStatus.RUNNING:
        return queue_manager.get_state()
    await queue_manager.start_queue(req.abort_on_error or False)
    return queue_manager.get_state()

@router.post("/pause")
async def pause_muxing():
    queue_manager.pause_queue()
    return queue_manager.get_state()

@router.post("/resume")
async def resume_muxing():
    queue_manager.resume_queue()
    return queue_manager.get_state()

@router.post("/stop")
async def stop_muxing():
    await queue_manager.stop_queue()
    return queue_manager.get_state()

@router.post("/clear")
async def clear_muxing_queue():
    state = await queue_manager.clear_queue(force=True)
    return state

@router.get("/status")
def get_mux_status():
    return queue_manager.get_state()
