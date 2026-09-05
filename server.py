"""Servidor local para la app del Cartel del Coyote."""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
sys.path.insert(0, str(ROOT))

from scripts.export_video import export_gif, export_mp4  # noqa: E402

app = Flask(__name__)


def _load_env_file():
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


_load_env_file()


def _fish_tts(text: str, reference_id: str = "") -> bytes:
    api_key = os.environ.get("FISH_AUDIO_API_KEY", "")
    if not api_key:
        raise RuntimeError("Falta FISH_AUDIO_API_KEY en .env")

    body = {
        "text": text,
        "format": "mp3",
        "prosody": {"speed": 1, "volume": 0, "normalize_loudness": True},
    }
    if reference_id:
        body["reference_id"] = reference_id

    last_error = "Fish Audio no disponible"
    preferred = os.environ.get("FISH_AUDIO_MODEL", "s2-pro")
    models = [preferred]
    if preferred != "s2.1-pro-free":
        models.append("s2.1-pro-free")

    for model in models:
        req = urllib.request.Request(
            "https://api.fish.audio/v1/tts",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "model": model,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            last_error = exc.read().decode("utf-8", errors="replace")[:200]
            if exc.code in (401, 402):
                break
    raise RuntimeError(last_error)


@app.route("/api/tts")
def api_tts():
    text = (request.args.get("text") or "").strip()[:200]
    voice = (request.args.get("voice") or "").strip()
    if not text:
        return jsonify({"error": "Falta el texto"}), 400

    try:
        audio = _fish_tts(text, voice)
        return send_file(
            __import__("io").BytesIO(audio),
            mimetype="audio/mpeg",
            download_name="voice.mp3",
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


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
    if os.environ.get("FISH_AUDIO_API_KEY"):
        model = os.environ.get("FISH_AUDIO_MODEL", "s2-pro")
        print(f"  Voz IA: Fish Audio ({model})")
    else:
        print("  Voz IA: sin token (crea .env con FISH_AUDIO_API_KEY)")
    print("  Abre: http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
