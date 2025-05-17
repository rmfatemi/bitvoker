import time
import yaml
import logging

from pathlib import Path
from typing import Dict, List, Optional

from fastapi.responses import JSONResponse, FileResponse
from fastapi import APIRouter, HTTPException, Query, Request

from bitvoker.config import Config
from bitvoker.utils import setup_logger
from bitvoker.database import get_notifications

logger = setup_logger("router")

api_router = APIRouter()


# ----------------------
# Config Endpoints
# ----------------------
@api_router.post("/api/config")
async def update_config(request: Request):
    form_data = await request.json()
    config_obj = Config()
    try:
        new_config_data = config_obj.config_data.copy()

        new_config_data["preprompt"] = form_data.get("preprompt", new_config_data.get("preprompt", ""))[:2048]
        new_config_data["enable_ai"] = form_data.get("enable_ai", False)
        new_config_data["show_original"] = (
            True if not new_config_data["enable_ai"] else form_data.get("show_original", True)
        )
        new_config_data["gui_theme"] = form_data.get("gui_theme", new_config_data.get("gui_theme", "dark"))

        channel_configs = {
            "telegram": ["chat_id", "token"],
            "discord": ["webhook_id", "token"],
            "slack": ["webhook_id", "token"],
            "gotify": ["server_url", "token"],
        }

        for channel, fields in channel_configs.items():
            channel_data = form_data.get(channel, {})
            new_config_data.setdefault(channel, {})["enabled"] = channel_data.get("enabled", False)
            for field in fields:
                new_config_data[channel][field] = channel_data.get(field, new_config_data[channel].get(field, ""))

        with open(config_obj.filename, "w", encoding="utf-8") as f:
            yaml.safe_dump(new_config_data, f, sort_keys=False)

        # dynamic TCP server configuration update
        tcp_server = request.app.state.tcp_server
        if tcp_server and hasattr(tcp_server, "config_manager"):
            fresh_config_manager = Config()
            tcp_server.config_manager = fresh_config_manager
            from bitvoker.ai import AI

            tcp_server.ai = AI(fresh_config_manager.preprompt) if fresh_config_manager.enable_ai else None
            from bitvoker.notifier import Notifier

            tcp_server.notifier = Notifier(fresh_config_manager.notification_channels)
            logger.info("TCP Server configuration dynamically updated.")
        else:
            logger.warning("Could not dynamically update TCP server config instance.")

        return {"success": True}
    except Exception as e:
        logger.error("Failed to update configuration: %s", e)
        return JSONResponse(content={"error": f"Failed to update config: {str(e)}"}, status_code=500)


@api_router.get("/api/config")
async def get_config():
    try:
        config_obj = Config()
        return config_obj.config_data
    except Exception as e:
        logger.error("Failed to retrieve configuration: %s", e)
        return JSONResponse(content={"error": f"Failed to retrieve config: {str(e)}"}, status_code=500)


# ----------------------
# Notifications Endpoints
# ----------------------
@api_router.get("/api/notifications")
def get_notifications_route(
    limit: int = Query(20), start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)
):
    try:
        notifs = get_notifications(limit, start_date or "", end_date or "")
        return {"notifications": notifs}
    except Exception as e:
        logger.error("Error retrieving notifications: %s", e)
        return JSONResponse(content={"notifications": [], "error": str(e)}, status_code=500)


# ----------------------
# Logs Endpoints
# ----------------------
class MemoryLogHandler(logging.Handler):
    def __init__(self, max_entries: int = 200):
        super().__init__()
        self.log_entries: List[Dict[str, str]] = []
        self.max_entries = max_entries

    def emit(self, record):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        self.log_entries.append(entry)
        if len(self.log_entries) > self.max_entries:
            self.log_entries.pop(0)

    def get_logs(self):
        return self.log_entries


memory_log_handler = MemoryLogHandler()
logging.getLogger().addHandler(memory_log_handler)


@api_router.get("/api/logs")
def get_logs(level: Optional[str] = Query(None)):
    logs = memory_log_handler.get_logs()
    if level and level.upper() != "ALL":
        logs = [log for log in logs if log["level"] == level.upper()]
    return {"logs": logs}


# ----------------------
# Catch-All for React App
# ----------------------
REACT_BUILD_DIR = Path(__file__).parent.parent / "web" / "build"


@api_router.get("/")
async def serve_index():
    index_path = REACT_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(content={"error": "Frontend not built"}, status_code=404)


@api_router.get("/{full_path:path}")
async def serve_react(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    requested_path = REACT_BUILD_DIR / full_path
    if requested_path.exists() and requested_path.is_file():
        return FileResponse(str(requested_path))
    index_path = REACT_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(content={"error": "Resource not found"}, status_code=404)
