"""Servidor local para la app del Cartel del Coyote."""

import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
sys.path.insert(0, str(ROOT))

from scripts.export_video import export_gif, export_mp4  # noqa: E402

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(PUBLIC, "index.html")


@app.route("/style.css")
def style_css():
    return send_from_directory(PUBLIC, "style.css")


@app.route("/app.js")
def app_js():
    return send_from_directory(PUBLIC, "app.js")


@app.route("/fonts/<path:filename>")
def font_files(filename):
    return send_from_directory(PUBLIC / "fonts", filename)


@app.route("/video/<path:filename>")
def video_files(filename):
    return send_from_directory(PUBLIC / "video", filename)


@app.route("/data/<path:filename>")
def data_files(filename):
    return send_from_directory(PUBLIC / "data", filename)


@app.route("/api/export/<fmt>", methods=["POST"])
def api_export(fmt):
    try:
        data = request.get_json(force=True)
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"error": "Escribe un texto para exportar"}), 400

        anim_id = int(data.get("animId", 1))
        color = data.get("color", "#1a1a1a")
        font_size = int(data.get("fontSize", 85))

        if fmt == "gif":
            out_path = export_gif(anim_id, text, color, font_size)
        elif fmt == "mp4":
            out_path = export_mp4(anim_id, text, color, font_size)
        else:
            return jsonify({"error": "Formato no soportado"}), 400

        return send_file(out_path, as_attachment=True, download_name=out_path.name)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    from scripts.calibrate_all import main as calibrate  # noqa: E402

    if not (PUBLIC / "data" / "animations.json").exists():
        calibrate()

    print("\n  Cartel del Coyote")
    print("  Abre: http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
