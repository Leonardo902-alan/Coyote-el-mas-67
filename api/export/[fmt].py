"""Exportación MP4/GIF en Vercel (serverless)."""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.export_video import export_gif, export_mp4  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            path = urlparse(self.path).path.rstrip("/")
            fmt = path.split("/")[-1]

            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) if length else b"{}")

            text = (body.get("text") or "").strip()
            if not text:
                self._json_error("Escribe un texto para exportar", 400)
                return

            anim_id = int(body.get("animId", 1))
            color = body.get("color", "#1a1a1a")
            font_size = int(body.get("fontSize", 85))

            if fmt == "gif":
                out_path = export_gif(anim_id, text, color, font_size)
            elif fmt == "mp4":
                out_path = export_mp4(anim_id, text, color, font_size)
            else:
                self._json_error("Formato no soportado", 400)
                return

            data = out_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{out_path.name}"',
            )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:
            self._json_error(str(exc), 500)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _json_error(self, message: str, status: int):
        payload = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
