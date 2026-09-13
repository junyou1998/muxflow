import asyncio
import os
import re
import shutil
import time
import zlib
from typing import Any, Callable, Dict, List, Optional
from ..config import LOGS_DIR
from .job_generator import JobGenerator

PROGRESS_REGEX = re.compile(r"Progress:\s*(\d+)%")

class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class QueueStatus:
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"

class QueueManager:
    def __init__(self):
        self.status = QueueStatus.IDLE
        self.jobs: List[Dict[str, Any]] = []
        self.current_job_index = -1
        self.current_process: Optional[asyncio.subprocess.Process] = None
        self.logs: List[str] = []
        self.max_logs = 1000
        self.broadcasters: List[Callable[[Dict[str, Any]], Any]] = []
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._stop_requested = False
        self._worker_task: Optional[asyncio.Task] = None
        self.start_time: Optional[float] = None
        self.total_bytes_processed = 0

    def subscribe(self, callback: Callable[[Dict[str, Any]], Any]):
        self.broadcasters.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], Any]):
        if callback in self.broadcasters:
            self.broadcasters.remove(callback)

    async def broadcast(self, message: Dict[str, Any]):
        for cb in list(self.broadcasters):
            try:
                res = cb(message)
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

    def _safe_create_task(self, coro):
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(coro)
        except RuntimeError:
            coro.close()
            return None

    def add_log(self, text: str):
        lines = text.strip().split("\n")
        for line in lines:
            if line:
                self.logs.append(line)
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        # Fire-and-forget broadcast log
        self._safe_create_task(self.broadcast({"type": "log", "text": text}))

    def get_state(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "current_job_index": self.current_job_index,
            "total_jobs": len(self.jobs),
            "jobs": [
                {
                    "id": idx,
                    "source_name": os.path.basename(j["source_path"]),
                    "output_name": os.path.basename(j["output_path"]),
                    "status": j["status"],
                    "progress": j.get("progress", 0),
                    "error": j.get("error"),
                    "tool": j.get("tool"),
                    "duration_sec": j.get("duration_sec", 0),
                }
                for idx, j in enumerate(self.jobs)
            ],
            "logs_tail": self.logs[-100:] if self.logs else [],
        }

    def add_jobs(self, jobs_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        added_count = 0
        start_id = len(self.jobs)
        for idx, conf in enumerate(jobs_configs):
            job_data = JobGenerator.generate_job(conf)
            job_data["status"] = JobStatus.PENDING
            job_data["progress"] = 0
            job_data["error"] = None
            job_data["duration_sec"] = 0
            job_data["queue_id"] = start_id + idx
            self.jobs.append(job_data)
            added_count += 1

        self.add_log(f"Added {added_count} job(s) to queue. Total: {len(self.jobs)}")
        self._safe_create_task(self.broadcast({"type": "queue_updated", "data": self.get_state()}))
        return self.get_state()

    def remove_job(self, job_idx: int) -> Dict[str, Any]:
        if 0 <= job_idx < len(self.jobs):
            target = self.jobs[job_idx]
            if target["status"] != JobStatus.RUNNING:
                self.jobs.pop(job_idx)
                if self.current_job_index > job_idx:
                    self.current_job_index -= 1
                self.add_log(f"Removed job: {os.path.basename(target['source_path'])}")
                self._safe_create_task(self.broadcast({"type": "queue_updated", "data": self.get_state()}))
        return self.get_state()

    async def start_queue(self, abort_on_error: bool = False):
        if self.status == QueueStatus.RUNNING:
            return

        has_pending = any(j["status"] == JobStatus.PENDING for j in self.jobs)
        if not has_pending:
            self.add_log("No pending jobs in queue.")
            return

        self.status = QueueStatus.RUNNING
        self._stop_requested = False
        self._pause_event.set()
        self.start_time = time.time()
        self.add_log("--- Starting Multiplexing Queue ---")
        
        await self.broadcast({"type": "queue_started", "data": self.get_state()})
        self._worker_task = asyncio.create_task(self._process_queue(abort_on_error))

    def pause_queue(self):
        if self.status == QueueStatus.RUNNING:
            self.status = QueueStatus.PAUSED
            self._pause_event.clear()
            self.add_log("--- Queue Paused ---")
            self._safe_create_task(self.broadcast({"type": "queue_paused", "data": self.get_state()}))

    def resume_queue(self):
        if self.status == QueueStatus.PAUSED:
            self.status = QueueStatus.RUNNING
            self._pause_event.set()
            self.add_log("--- Queue Resumed ---")
            self._safe_create_task(self.broadcast({"type": "queue_resumed", "data": self.get_state()}))

    async def stop_queue(self):
        self._stop_requested = True
        self.status = QueueStatus.STOPPED
        self._pause_event.set()
        
        if self.current_process and self.current_process.returncode is None:
            try:
                self.current_process.terminate()
                await asyncio.sleep(0.5)
                if self.current_process.returncode is None:
                    self.current_process.kill()
            except Exception:
                pass

        if self._worker_task:
            self._worker_task.cancel()

        # Mark pending/running jobs as cancelled
        for j in self.jobs:
            if j["status"] in [JobStatus.PENDING, JobStatus.RUNNING]:
                j["status"] = JobStatus.CANCELLED

        self.add_log("--- Queue Stopped by User ---")
        await self.broadcast({"type": "queue_stopped", "data": self.get_state()})

    async def clear_queue(self, force: bool = True):
        if self.current_process and self.current_process.returncode is None:
            try:
                self.current_process.terminate()
                await asyncio.sleep(0.3)
                if self.current_process.returncode is None:
                    self.current_process.kill()
            except Exception:
                pass

        if self._worker_task:
            self._worker_task.cancel()

        self.jobs = []
        self.current_job_index = -1
        self.logs = []
        self.status = QueueStatus.IDLE
        self._stop_requested = False
        await self.broadcast({"type": "queue_cleared", "data": self.get_state()})
        return self.get_state()

    async def _process_queue(self, abort_on_error: bool):
        try:
            while True:
                if self._stop_requested:
                    break

                # Wait if paused
                await self._pause_event.wait()
                if self._stop_requested:
                    break

                # Find next pending job
                next_idx = next((i for i, j in enumerate(self.jobs) if j["status"] == JobStatus.PENDING), None)
                if next_idx is None:
                    break

                idx = next_idx
                job = self.jobs[idx]
                self.current_job_index = idx
                job["status"] = JobStatus.RUNNING
                job["progress"] = 0
                job_start_time = time.time()
                
                await self.broadcast({"type": "job_started", "job_index": idx, "data": self.get_state()})
                self.add_log(f"[{idx+1}/{len(self.jobs)}] Processing: {os.path.basename(job['source_path'])} via {job['tool']}")

                success = await self._run_single_job(job)
                job["duration_sec"] = round(time.time() - job_start_time, 1)

                if success:
                    job["status"] = JobStatus.COMPLETED
                    job["progress"] = 100
                    self.add_log(f"[{idx+1}/{len(self.jobs)}] Completed in {job['duration_sec']}s")
                    
                    # Post-processing: Overwrite atomic replace & CRC32
                    await self._post_process_job(job)
                else:
                    job["status"] = JobStatus.FAILED
                    self.add_log(f"[{idx+1}/{len(self.jobs)}] FAILED: {job.get('error')}")
                    if abort_on_error:
                        self.add_log("Abort on errors is enabled. Stopping queue.")
                        break

                await self.broadcast({"type": "job_finished", "job_index": idx, "data": self.get_state()})

            self.status = QueueStatus.IDLE
            self.add_log("--- All Jobs Finished ---")
            await self.broadcast({"type": "queue_finished", "data": self.get_state()})

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.add_log(f"Queue execution exception: {str(e)}")
            self.status = QueueStatus.STOPPED
            await self.broadcast({"type": "queue_error", "error": str(e), "data": self.get_state()})

    async def _run_single_job(self, job: Dict[str, Any]) -> bool:
        cmd = job["cmd"]
        self.add_log(f"Executing: {' '.join(cmd)}")
        try:
            self.current_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )

            while True:
                line = await self.current_process.stdout.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace").strip()
                if not decoded:
                    continue

                # Parse progress
                m = PROGRESS_REGEX.search(decoded)
                if m:
                    pct = int(m.group(1))
                    job["progress"] = pct
                    await self.broadcast({
                        "type": "job_progress",
                        "job_index": self.current_job_index,
                        "progress": pct
                    })
                else:
                    self.add_log(decoded)

            await self.current_process.wait()
            return self.current_process.returncode == 0 or (job["tool"] == "mkvpropedit" and self.current_process.returncode in [0, 1])

        except Exception as e:
            job["error"] = str(e)
            return False

    async def _post_process_job(self, job: Dict[str, Any]):
        output_file = job["temp_output_path"] if job.get("temp_output_path") else job["output_path"]

        # If overwrite was requested
        if job.get("is_overwrite") and job.get("temp_output_path"):
            try:
                # Replace source with temp output
                shutil.move(job["temp_output_path"], job["output_path"])
                output_file = job["output_path"]
                self.add_log(f"Replaced original file: {job['output_path']}")
            except Exception as e:
                self.add_log(f"Error replacing original file: {e}")

        # If add_crc was requested
        if job.get("add_crc") and os.path.exists(output_file):
            try:
                self.add_log(f"Calculating CRC32 for {os.path.basename(output_file)}...")
                crc_val = await self._calculate_crc32(output_file)
                crc_hex = format(crc_val & 0xFFFFFFFF, "08X")

                dir_name = os.path.dirname(output_file)
                base_name, ext = os.path.splitext(os.path.basename(output_file))
                new_filename = f"{base_name} [{crc_hex}]{ext}"
                new_full_path = os.path.join(dir_name, new_filename)

                os.rename(output_file, new_full_path)
                job["output_path"] = new_full_path
                self.add_log(f"Appended CRC32: {new_filename}")
            except Exception as e:
                self.add_log(f"CRC32 calculation error: {e}")

    async def _calculate_crc32(self, file_path: str) -> int:
        def compute():
            crc = 0
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 1024 * 4): # 4MB chunk
                    crc = zlib.crc32(chunk, crc)
            return crc
        return await asyncio.to_thread(compute)

# Global singleton queue manager
queue_manager = QueueManager()
