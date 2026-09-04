"""Calibra posición exacta del texto en cada animación."""

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
VIDEO_DIR = PUBLIC / "video"
OUT_PATH = PUBLIC / "data" / "animations.json"
DEBUG_DIR = ROOT / "analysis" / "calibration"

TEXT_START = {1: 22, 2: 34, 3: 32, 4: 31}


def get_sign_template():
    cap = cv2.VideoCapture(str(VIDEO_DIR / "coyote1.mp4"))
    cap.set(cv2.CAP_PROP_POS_FRAMES, 40)
    _, frame = cap.read()
    cap.release()
    return cv2.cvtColor(frame[295:495, 395:885], cv2.COLOR_BGR2GRAY)


def find_sign_in_frame(frame, template):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    th, tw = template.shape
    h, w = gray.shape
    mx, my = int(w * 0.15), int(h * 0.20)
    region = gray[my : h - int(h * 0.15), mx : w - int(w * 0.15)]
    result = cv2.matchTemplate(region, template, cv2.TM_CCOEFF_NORMED)
    _, conf, _, loc = cv2.minMaxLoc(result)
    return conf, loc[0] + mx, loc[1] + my, tw, th


# Centro vertical del cartel — un poco más abajo + área más alta para varias líneas
TEXT_CENTER_RATIO = 0.86


def sign_to_text_area(sx, sy, tw, th):
    """Área de texto multilínea centrada en el cartel."""
    cx = sx + tw / 2
    cy = sy + th * TEXT_CENTER_RATIO
    text_w = int(tw * 0.72)
    text_h = int(th * 0.54)

    return {
        "x": int(round(cx - text_w / 2)),
        "y": int(round(cy - text_h / 2)),
        "w": text_w,
        "h": text_h,
        "centerX": int(round(cx)),
        "centerY": int(round(cy)),
    }


def calibrate_clip(clip_id: int, template):
    path = VIDEO_DIR / f"coyote{clip_id}.mp4"
    cap = cv2.VideoCapture(str(path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24

    samples = [TEXT_START[clip_id], total - 3, total - 2, total - 1]
    areas, best_conf, best_loc, th, tw = [], 0, None, *template.shape

    for idx in samples:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        conf, sx, sy, _, _ = find_sign_in_frame(frame, template)
        if conf > 0.45:
            areas.append(sign_to_text_area(sx, sy, tw, th))
            if conf > best_conf:
                best_conf, best_loc = conf, (sx, sy)

    cap.release()

    if areas:
        text_box = {k: int(round(np.mean([a[k] for a in areas]))) for k in ("x", "y", "w", "h", "centerX", "centerY")}
        sx, sy = best_loc
        sign_box = {"x": int(sx), "y": int(sy), "w": int(tw), "h": int(th)}
    else:
        text_box = {"x": 448, "y": 347, "w": 384, "h": 120, "centerX": 640, "centerY": 407}
        sign_box = {"x": 395, "y": 295, "w": 490, "h": 200}

    return {
        "id": clip_id,
        "file": f"coyote{clip_id}.mp4",
        "label": f"Animación {clip_id}",
        "totalFrames": total,
        "fps": fps,
        "textStartFrame": TEXT_START[clip_id],
        "textStartTime": round(TEXT_START[clip_id] / fps, 3),
        "textBox": text_box,
        "signBox": sign_box,
        "confidence": round(best_conf, 3),
    }


def save_debug(cfg):
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(VIDEO_DIR / cfg["file"]))
    cap.set(cv2.CAP_PROP_POS_FRAMES, cfg["textStartFrame"])
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return

    t = cfg["textBox"]
    s = cfg["signBox"]
    cv2.rectangle(frame, (s["x"], s["y"]), (s["x"] + s["w"], s["y"] + s["h"]), (255, 180, 0), 1)
    cv2.rectangle(frame, (t["x"], t["y"]), (t["x"] + t["w"], t["y"] + t["h"]), (0, 255, 0), 2)
    cv2.drawMarker(frame, (t["centerX"], t["centerY"]), (255, 0, 0), cv2.MARKER_CROSS, 24, 2)
    cv2.imwrite(str(DEBUG_DIR / f"anim{cfg['id']}_cal.jpg"), frame)


def main():
    template = get_sign_template()
    configs = [calibrate_clip(i, template) for i in range(1, 5)]
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2, ensure_ascii=False)
    for cfg in configs:
        save_debug(cfg)
        t = cfg["textBox"]
        print(f"Anim {cfg['id']}: center=({t['centerX']},{t['centerY']}) box={t['w']}x{t['h']}")


if __name__ == "__main__":
    main()
