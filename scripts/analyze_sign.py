import cv2
import json
import numpy as np
from pathlib import Path

VIDEO_PATH = Path(r"d:\Descargas LeoMaster\Coyote_holding_blank_sign_202609041426.mp4")
OUT_DIR = Path(__file__).resolve().parent.parent / "analysis"
OUT_DIR.mkdir(exist_ok=True)

# Sign text area on frame 120 (blank wooden sign center)
DEFAULT_SIGN = {
    "x": 395,
    "y": 295,
    "w": 490,
    "h": 200,
    "angle": 0,
}


def load_template(cap):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 120)
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Could not read template frame")
    sign = frame[280:480, 395:885]
    cv2.imwrite(str(OUT_DIR / "sign_template.jpg"), sign)
    return sign


def track_with_template(cap, template):
    positions = []
    frame_idx = 0
    prev_box = None
    th, tw = template.shape[:2]

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tmpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        search = gray
        if prev_box:
            px, py, pw, ph = prev_box
            margin = 80
            x1 = max(0, px - margin)
            y1 = max(0, py - margin)
            x2 = min(frame.shape[1], px + pw + margin)
            y2 = min(frame.shape[0], py + ph + margin)
            search = gray[y1:y2, x1:x2]
            offset = (x1, y1)
        else:
            offset = (0, 0)

        if search.shape[0] < th or search.shape[1] < tw:
            positions.append({"frame": frame_idx, "visible": False})
            frame_idx += 1
            continue

        result = cv2.matchTemplate(search, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.35:
            x = int(max_loc[0] + offset[0])
            y = int(max_loc[1] + offset[1])
            # Text area is inner portion of sign
            text_x = x + int(tw * 0.08)
            text_y = y + int(th * 0.18)
            text_w = int(tw * 0.84)
            text_h = int(th * 0.64)
            positions.append(
                {
                    "frame": frame_idx,
                    "visible": True,
                    "confidence": round(float(max_val), 3),
                    "sign": {"x": x, "y": y, "w": tw, "h": th},
                    "text": {"x": text_x, "y": text_y, "w": text_w, "h": text_h},
                }
            )
            prev_box = (x, y, tw, th)
        else:
            positions.append({"frame": frame_idx, "visible": False, "confidence": round(float(max_val), 3)})
            prev_box = None

        frame_idx += 1

    return positions


def fill_gaps(positions):
    """Interpolate missing frames using nearest visible neighbors."""
    filled = positions[:]
    visible_indices = [i for i, p in enumerate(filled) if p.get("visible")]

    if not visible_indices:
        for i, p in enumerate(filled):
            filled[i] = {**p, **DEFAULT_SIGN, "visible": i >= 90}
        return filled

    first = visible_indices[0]
    last = visible_indices[-1]

    for i in range(len(filled)):
        if filled[i].get("visible"):
            continue
        # Before sign appears: hidden
        if i < first:
            filled[i] = {"frame": i, "visible": False}
            continue
        # After sign disappears
        if i > last:
            filled[i] = {"frame": i, "visible": False}
            continue
        # Interpolate between neighbors
        left = max(j for j in visible_indices if j < i)
        right = min(j for j in visible_indices if j > i)
        t = (i - left) / (right - left)
        left_p = filled[left]
        right_p = filled[right]
        interp = {"frame": i, "visible": True, "confidence": 0.5}
        for key in ("sign", "text"):
            interp[key] = {}
            for k in left_p[key]:
                interp[key][k] = int(left_p[key][k] + (right_p[key][k] - left_p[key][k]) * t)
        filled[i] = interp

    return filled


def main():
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    template = load_template(cap)
    positions = track_with_template(cap, template)
    cap.release()

    positions = fill_gaps(positions)
    visible = [p for p in positions if p.get("visible")]

    print(f"Total frames: {len(positions)}")
    print(f"Visible (with text): {len(visible)}")
    if visible:
        print(f"First text frame: {visible[0]['frame']}")
        print(f"Sample text box frame 120: {visible[120]['text']}")

    out_path = OUT_DIR / "sign_positions.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(positions, f, indent=2)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
