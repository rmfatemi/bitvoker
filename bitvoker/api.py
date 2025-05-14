import time
import yaml
import logging
import uvicorn
import threading
import socketserver
from pathlib import Path
from typing import Optional, Dict, List

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from bitvoker.ai import AI
from bitvoker.config import Config
from bitvoker.handler import Handler
from bitvoker.notifier import Notifier
from bitvoker.logger import setup_logger
from bitvoker.database import get_notifications
from bitvoker.constants import TCP_SERVER_PORT, UI_SERVER_PORT, SERVER_HOST

logger = setup_logger("api")
tcp_server_instance = None


class CustomThreadingTCPServer(socketserver.ThreadingTCPServer):
    def __init__(
        self,
        server_address,
        RequestHandlerClass,
        bind_and_activate=True,
        config_manager_instance=None,
        ai_instance=None,
        notifier_instance=None,
    ):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.config_manager = config_manager_instance
        self.ai = ai_instance
        self.notifier = notifier_instance


def run_tcp_server():
    global tcp_server_instance
    try:
        config_manager = Config()
        notifier = Notifier(config_manager.notification_channels)
        ai = AI(config_manager.preprompt) if config_manager.enable_ai else None
        socketserver.TCPServer.allow_reuse_address = True

        tcp_server_instance = CustomThreadingTCPServer(
            (SERVER_HOST, TCP_SERVER_PORT),
            Handler,
            config_manager_instance=config_manager,
            ai_instance=ai,
            notifier_instance=notifier,
        )
        logger.info("TCP Server listening on %s:%s ...", SERVER_HOST, TCP_SERVER_PORT)
        tcp_server_instance.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start TCP server: {str(e)}")


class MemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_entries: List[Dict[str, str]] = []
        self.max_entries = 200

    def emit(self, record):
        self.log_entries.append(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created)),
                "level": record.levelname,
                "message": record.getMessage(),
            }
        )
        if len(self.log_entries) > self.max_entries:
            self.log_entries.pop(0)

    def get_logs(self):
        return self.log_entries


mem_handler = MemoryLogHandler()
logging.getLogger().addHandler(mem_handler)


class BitvokerAPI:
    def __init__(self):
        self.server_thread = threading.Thread(target=run_tcp_server, daemon=True)

    def start(self):
        self.server_thread.start()
        uvicorn.run(app, host=SERVER_HOST, port=UI_SERVER_PORT)

    def shutdown(self):
        if tcp_server_instance:
            tcp_server_instance.shutdown()
            logger.info("TCP Server shutdown complete.")


# Define paths and app
REACT_BUILD_DIR = Path(__file__).parent.parent / "web" / "build"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/config")
def get_config():
    return {"config": Config().config_data}


@app.post("/api/config")
async def update_config(request: Request):
    form_data = await request.json()
    config_manager = Config()

    try:
        new_config_data = config_manager.config_data.copy()

        # Handle general settings
        preprompt_val = form_data.get("preprompt", new_config_data.get("preprompt", ""))
        new_config_data["preprompt"] = preprompt_val[:2048] if len(preprompt_val) > 2048 else preprompt_val
        new_config_data["enable_ai"] = form_data.get("enable_ai", False)
        new_config_data["show_original"] = (
            True if not new_config_data["enable_ai"] else form_data.get("show_original", True)
        )
        new_config_data["gui_theme"] = form_data.get("gui_theme", new_config_data.get("gui_theme", "dark"))

        # Handle notification channels
        channel_configs = {
            "telegram": ["bot_token", "chat_id"],
            "slack": ["webhook_id", "token"],
            "discord": ["webhook_url", "token"],
            "gotify": ["server_url", "app_token"],
        }

        for channel, fields in channel_configs.items():
            if channel not in new_config_data:
                new_config_data[channel] = {}

            new_config_data[channel]["enabled"] = form_data.get(f"{channel}_enabled", False)

            for field in fields:
                field_key = f"{channel}_{field}"
                new_config_data[channel][field] = form_data.get(
                    field_key, new_config_data.get(channel, {}).get(field, "")
                )

        # Save config and update running services
        with open(config_manager.filename, "w", encoding="utf-8") as f:
            yaml.safe_dump(new_config_data, f, sort_keys=False)

        if tcp_server_instance and hasattr(tcp_server_instance, "config_manager"):
            fresh_config_manager = Config()
            tcp_server_instance.config_manager = fresh_config_manager
            tcp_server_instance.ai = AI(fresh_config_manager.preprompt) if fresh_config_manager.enable_ai else None
            tcp_server_instance.notifier = Notifier(fresh_config_manager.notification_channels)
            logger.info("TCP Server configuration dynamically updated.")
        else:
            logger.warning("Could not dynamically update TCP server config instance.")

        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to save configuration: {str(e)}")
        return JSONResponse(content={"error": f"Failed to save: {str(e)}"}, status_code=500)


@app.get("/api/notifications")
def get_notifications_route(
    limit: int = Query(20), start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)
):
    try:
        notifs = get_notifications(limit, start_date or "", end_date or "")
        return {"notifications": notifs}
    except Exception as e:
        logger.error(f"Error retrieving notifications: {str(e)}")
        return JSONResponse(content={"notifications": [], "error": str(e)}, status_code=500)


@app.get("/api/logs")
def get_logs(level: Optional[str] = Query(None)):
    logs = mem_handler.get_logs()
    if level and level != "ALL":
        logs = [log for log in logs if log["level"] == level]
    return {"logs": logs}


# Serve React static files - with error handling
static_dir = REACT_BUILD_DIR / "static"
if static_dir.exists() and static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}")


# React file serving routes
@app.get("/")
async def serve_index():
    index_path = REACT_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(content={"error": "Frontend not built"}, status_code=404)


@app.get("/manifest.json")
async def serve_manifest():
    manifest_path = REACT_BUILD_DIR / "manifest.json"
    if manifest_path.exists():
        return FileResponse(str(manifest_path))
    return JSONResponse(status_code=404)


@app.get("/asset-manifest.json")
async def serve_asset_manifest():
    asset_path = REACT_BUILD_DIR / "asset-manifest.json"
    if asset_path.exists():
        return FileResponse(str(asset_path))
    return JSONResponse(status_code=404)


@app.get("/{full_path:path}")
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


def main():
    try:
        BitvokerAPI().start()
    except KeyboardInterrupt:
        BitvokerAPI().shutdown()
        logger.info("Application shutdown complete.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")


if __name__ == "__main__":
    main()
