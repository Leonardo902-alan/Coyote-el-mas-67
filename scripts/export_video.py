"""Exporta clips del coyote con texto multilínea en el cartel."""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.text_layout import wrap_words  # noqa: E402

PUBLIC_DIR = ROOT / "public"
VIDEO_DIR = PUBLIC_DIR / "video"
DATA_PATH = PUBLIC_DIR / "data" / "animations.json"
OUTPUT_DIR = Path("/tmp") if os.environ.get("VERCEL") else ROOT / "output"
FONT_PATH = PUBLIC_DIR / "fonts" / "Bangers-Regular.ttf"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def load_config(anim_id: int) -> dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        configs = json.load(f)
    for cfg in configs:
        if cfg["id"] == anim_id:
            return cfg
    raise ValueError(f"Animación {anim_id} no encontrada")


def load_font(size: int):
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"No se encontró la fuente Bangers en {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def get_center(text_box: dict) -> tuple[int, int]:
    return text_box.get("centerX", text_box["x"] + text_box["w"] // 2), text_box.get(
        "centerY", text_box["y"] + text_box["h"] // 2
    )


def draw_text_on_frame(frame, text: str, text_box: dict, color_rgb: tuple, base_size: int):
    cx, cy = get_center(text_box)
    w, h = text_box["w"], text_box["h"]

    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    font_size = max(16, base_size)
    font = load_font(font_size)

    def measure(line: str) -> float:
        bbox = draw.textbbox((0, 0), line, font=font)
        return bbox[2] - bbox[0]

    while font_size >= 14:
        font = load_font(font_size)
        lines = wrap_words(text, measure, w * 0.92)
        line_height = font_size * 1.12
        total_h = len(lines) * line_height
        widest = max(measure(line) for line in lines)
        if widest <= w * 0.92 and total_h <= h * 0.88:
            break
        font_size -= 1

    lines = wrap_words(text, measure, w * 0.92)
    line_height = font_size * 1.12
    total_h = len(lines) * line_height
    start_y = cy - total_h / 2 + line_height / 2
    outline = max(1, font_size // 40)

    for i, line in enumerate(lines):
        ly = start_y + i * line_height
        for ox in range(-outline, outline + 1):
            for oy in range(-outline, outline + 1):
                if ox or oy:
                    draw.text((cx + ox, ly + oy), line, font=font, fill=(25, 25, 25), anchor="mm")
        draw.text((cx, ly), line, font=font, fill=color_rgb, anchor="mm")

    frame[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def render_frames(anim_id: int, text: str, color_hex: str, font_size: int) -> tuple[list, float]:
    cfg = load_config(anim_id)
    text = text.strip()
    if not text:
        raise ValueError("El texto no puede estar vacío")

    cap = cv2.VideoCapture(str(VIDEO_DIR / cfg["file"]))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    color = hex_to_rgb(color_hex)
    frames = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx >= cfg["textStartFrame"]:
            draw_text_on_frame(frame, text, cfg["textBox"], color, font_size)
        frames.append(frame.copy())
        frame_idx += 1

    cap.release()
    return frames, fps


def write_h264_mp4(frames: list, fps: float, out_path: Path):
    h, w = frames[0].shape[:2]
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()

    try:
        writer = cv2.VideoWriter(str(tmp_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        for frame in frames:
            writer.write(frame)
        writer.release()

        cmd = [
            FFMPEG, "-y", "-i", str(tmp_path),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-profile:v", "baseline", "-level", "3.1",
            "-movflags", "+faststart", "-crf", "23", "-an",
            str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr[-500:] if result.stderr else "Error ffmpeg")
    finally:
        tmp_path.unlink(missing_ok=True)


def export_mp4(anim_id: int, text: str, color_hex: str = "#1a1a1a", font_size: int = 72) -> Path:
    frames, fps = render_frames(anim_id, text, color_hex, font_size)
    if not frames:
        raise ValueError("No se pudieron leer frames del video")

    OUTPUT_DIR.mkdir(exist_ok=True)
    safe = re.sub(r"[^\w\-]", "_", text)[:25]
    out_path = OUTPUT_DIR / f"coyote{anim_id}_{safe}.mp4"
    write_h264_mp4(frames, fps, out_path)
    return out_path


def export_gif(anim_id: int, text: str, color_hex: str = "#1a1a1a", font_size: int = 72) -> Path:
    frames, fps = render_frames(anim_id, text, color_hex, font_size)
    if not frames:
        raise ValueError("No se pudieron leer frames del video")

    OUTPUT_DIR.mkdir(exist_ok=True)
    safe = re.sub(r"[^\w\-]", "_", text)[:25]
    out_path = OUTPUT_DIR / f"coyote{anim_id}_{safe}.gif"

    pil_frames = [
        Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).resize((640, 360), Image.Resampling.LANCZOS)
        for f in frames
    ]
    duration_ms = max(1, int(1000 / fps))
    pil_frames[0].save(
        out_path, save_all=True, append_images=pil_frames[1:],
        duration=duration_ms, loop=0, optimize=True,
    )
    return out_path


if __name__ == "__main__":
    aid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    txt = sys.argv[2] if len(sys.argv) > 2 else "Hola"
    fmt = sys.argv[3] if len(sys.argv) > 3 else "mp4"
    if fmt == "gif":
        print(export_gif(aid, txt))
    else:
        print(export_mp4(aid, txt))
