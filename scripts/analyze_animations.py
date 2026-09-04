"""Detecta cuándo termina la animación y posiciona el texto en cada clip."""

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "video"
OUT_PATH = ROOT / "data" / "animations.json"

MOTION_THRESHOLD = 1.2
SIGN_CONFIDENCE = 0.42
ANIMATION_MOTION = 3.0


def load_sign_template():
    cap = cv2.VideoCapture(str(SOURCE_DIR / "coyote1.mp4"))
    cap.set(cv2.CAP_PROP_POS_FRAMES, 40)
    _, frame = cap.read()
    cap.release()
    return cv2.cvtColor(frame[280:500, 390:890], cv2.COLOR_BGR2GRAY)


def sign_info(gray, template):
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_val >= SIGN_CONFIDENCE, max_val, max_loc


def build_text_box(max_loc, template_shape):
    th, tw = template_shape
    sx, sy = max_loc
    return {
        "x": int(sx + tw * 0.10),
        "y": int(sy + th * 0.42),
        "w": int(tw * 0.80),
        "h": int(th * 0.45),
    }


def find_text_start(motion, visible):
    """Primer frame quieto tras la última animación fuerte."""
    last_anim = 0
    for i, m in enumerate(motion):
        if m > ANIMATION_MOTION:
            last_anim = i

    for i in range(last_anim + 1, len(motion)):
        if not visible[i] or motion[i] >= MOTION_THRESHOLD:
            continue
        stable = True
        for j in range(i, min(i + 3, len(motion))):
            if motion[j] >= MOTION_THRESHOLD or not visible[j]:
                stable = False
                break
        if stable:
            return i

    for i, m in enumerate(motion):
        if visible[i] and m < MOTION_THRESHOLD:
            return i
    return max(0, len(motion) - 1)


def analyze_clip(clip_id: int, template):
    path = SOURCE_DIR / f"coyote{clip_id}.mp4"
    cap = cv2.VideoCapture(str(path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    motion = [999.0]
    visible = []
    prev_gray = None

    for _ in range(total):
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            motion.append(float(np.mean(cv2.absdiff(prev_gray, gray))))
        prev_gray = gray
        is_vis, _, _ = sign_info(gray, template)
        visible.append(is_vis)

    cap.release()

    text_start = find_text_start(motion, visible)

    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, text_start)
    _, frame = cap.read()
    cap.release()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, _, loc = sign_info(gray, template)
    th, tw = template.shape

    return {
        "id": clip_id,
        "file": f"coyote{clip_id}.mp4",
        "label": f"Animación {clip_id}",
        "totalFrames": total,
        "fps": 24,
        "textStartFrame": text_start,
        "textBox": build_text_box(loc, template.shape),
        "signBox": {"x": int(loc[0]), "y": int(loc[1]), "w": int(tw), "h": int(th)},
    }


def main():
    template = load_sign_template()
    configs = [analyze_clip(i, template) for i in range(1, 5)]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2, ensure_ascii=False)

    for cfg in configs:
        print(
            f"{cfg['label']}: animación 0-{cfg['textStartFrame'] - 1}, "
            f"texto {cfg['textStartFrame']}-{cfg['totalFrames'] - 1}"
        )
    print(f"Guardado en {OUT_PATH}")


if __name__ == "__main__":
    main()
