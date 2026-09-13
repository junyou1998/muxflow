import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_DIR
from .services.queue_manager import queue_manager
from .api import files, videos, mux, presets

app = FastAPI(title="MuxFlow - MKV Batch Muxing Suite", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(videos.router)
app.include_router(mux.router)
app.include_router(presets.router)

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Send current state immediately upon connection
    await websocket.send_text(json.dumps({
        "type": "initial_state",
        "data": queue_manager.get_state()
    }))

    async def broadcast_handler(msg):
        try:
            await websocket.send_text(json.dumps(msg))
        except Exception:
            pass

    queue_manager.subscribe(broadcast_handler)
    try:
        while True:
            # Keep alive and listen for ping/client messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        queue_manager.unsubscribe(broadcast_handler)

# Serve Frontend static assets
if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")

    @app.get("/logo.png")
    @app.get("/favicon.ico")
    async def serve_logo():
        logo_path = os.path.join(FRONTEND_DIR, "logo.png")
        if os.path.exists(logo_path):
            return FileResponse(logo_path, media_type="image/png")
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/")
    async def serve_index():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        return FileResponse(index_file)
