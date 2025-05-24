import time
import logging

from typing import Dict, List, Optional
from pathlib import Path

from fastapi.responses import JSONResponse, FileResponse
from fastapi import APIRouter, HTTPException, Query, Request

from bitvoker.config import Config
from bitvoker.logger import setup_logger
from bitvoker.constants import REACT_BUILD_DIR
from bitvoker.database import get_notifications
from bitvoker.refresher import refresh_components

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
        # Handle AI configuration
        if "ai" in form_data:
            ai_config = form_data.get("ai", {})
            config_obj.update_ai_config(ai_config)

        # Handle rules
        if "rules" in form_data:
            for idx, rule in enumerate(form_data.get("rules", [])):
                if idx < len(config_obj.get_rules()):
                    config_obj.update_rule(idx, rule)
                else:
                    config_obj.add_rule(rule)

            # Delete any extra rules
            while len(config_obj.get_rules()) > len(form_data.get("rules", [])):
                config_obj.delete_rule(len(config_obj.get_rules()) - 1)

        # Handle notification channels
        if "notification_channels" in form_data:
            for idx, channel in enumerate(form_data.get("notification_channels", [])):
                if idx < len(config_obj.get_channels()):
                    config_obj.update_channel(idx, channel)
                else:
                    config_obj.add_channel(channel)

            # Delete any extra channels
            while len(config_obj.get_channels()) > len(form_data.get("notification_channels", [])):
                config_obj.delete_channel(len(config_obj.get_channels()) - 1)

        # Theme settings
        if "gui_theme" in form_data:
            if "gui" not in config_obj.config_data:
                config_obj.config_data["gui"] = {}
            config_obj.config_data["gui"]["theme"] = form_data.get("gui_theme", "dark")
            config_obj.save()

        refresh_components(request.app)
        return {"success": True}
    except Exception as e:
        logger.error(f"failed to update configuration: {e}")
        return JSONResponse(content={"error": f"failed to update config: {str(e)}"}, status_code=500)


@api_router.get("/api/config")
async def get_config():
    try:
        config_obj = Config()
        return config_obj.config_data
    except Exception as e:
        logger.error(f"failed to retrieve configuration: {e}")
        return JSONResponse(content={"error": f"failed to retrieve config: {str(e)}"}, status_code=500)


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
        logger.error(f"error retrieving notifications: {e}")
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


@api_router.get("/")
async def serve_index():
    index_path = Path(REACT_BUILD_DIR) / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(content={"error": "frontend not built"}, status_code=404)


@api_router.get("/{full_path:path}")
async def serve_react(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    requested_path = Path(REACT_BUILD_DIR) / full_path
    if requested_path.exists() and requested_path.is_file():
        return FileResponse(str(requested_path))
    index_path = Path(REACT_BUILD_DIR) / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(content={"error": "resource not found"}, status_code=404)
