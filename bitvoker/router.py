import time
import yaml
import logging

from pathlib import Path
from typing import Dict, List, Optional

from fastapi.responses import JSONResponse, FileResponse
from fastapi import APIRouter, HTTPException, Query, Request

from bitvoker.config import Config
from bitvoker.logger import setup_logger
from bitvoker.database import get_notifications
from bitvoker.components import refresh_server_components


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

        # dynamic tcp server configuration update
        try:
            if hasattr(request.app.state, "secure_tcp_server"):
                refresh_server_components(request.app.state.secure_tcp_server, force_new_config=True)
                logger.info("secure tcp server configuration dynamically updated")
            else:
                logger.warning("secure tcp server not found in application state")

            if hasattr(request.app.state, "plain_tcp_server"):
                refresh_server_components(request.app.state.plain_tcp_server, force_new_config=True)
                logger.info("plain tcp server configuration dynamically updated")
            else:
                logger.warning("plain tcp server not found in application state")

            request.app.state.tcp_servers = {
                "secure": (
                    request.app.state.secure_tcp_server if hasattr(request.app.state, "secure_tcp_server") else None
                ),
                "plain": request.app.state.plain_tcp_server if hasattr(request.app.state, "plain_tcp_server") else None,
            }

            return {"success": True}
        except Exception as e:
            logger.error(f"failed to update server configuration: {e}")
            return JSONResponse(content={"error": f"failed to update config: {str(e)}"}, status_code=500)

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
REACT_BUILD_DIR = Path(__file__).parent.parent / "web" / "build"


@api_router.get("/")
async def serve_index():
    index_path = REACT_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(content={"error": "frontend not built"}, status_code=404)


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
    return JSONResponse(content={"error": "resource not found"}, status_code=404)
