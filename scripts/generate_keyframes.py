"""Genera posiciones del cartel por frame usando keyframes + interpolación."""

import json
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "public" / "data" / "sign_positions.json"

# Keyframes: (frame, visible, sign_x, sign_y, sign_w, sign_h)
# Basado en análisis visual del video (10s, 240 frames, 24fps)
KEYFRAMES = [
    (0, True, 350, 370, 500, 140),    # Cartel detrás, motion blur
    (10, True, 390, 310, 490, 195),   # Sacando cartel
    (20, True, 395, 310, 490, 200),   # Cartel visible
    (35, True, 395, 310, 490, 200),
    (50, True, 395, 310, 490, 200),
    (58, False, 0, 0, 0, 0),          # Guarda cartel detrás
    (62, False, 0, 0, 0, 0),
    (68, False, 0, 0, 0, 0),
    (72, True, 400, 305, 480, 210),   # Saca cartel otra vez
    (80, True, 395, 310, 490, 200),
    (100, True, 395, 310, 490, 200),
    (130, True, 395, 310, 490, 200),  # Cartel estable
    (155, True, 395, 307, 490, 203),  # Pequeño temblor
    (160, True, 395, 313, 490, 197),
    (165, True, 395, 310, 490, 200),
    (175, True, 395, 310, 490, 200),
    (185, True, 395, 310, 490, 200),
    (192, False, 0, 0, 0, 0),         # Esconde cartel
    (198, True, 360, 320, 420, 170),  # Motion blur lateral
    (205, True, 390, 310, 490, 200),
    (215, True, 395, 310, 490, 200),
    (230, True, 395, 310, 490, 200),
    (239, True, 395, 310, 490, 200),
]

TOTAL_FRAMES = 240


def lerp(a, b, t):
    return a + (b - a) * t


def sign_to_text(sign):
    x, y, w, h = sign
    return {
        "x": int(x + w * 0.08),
        "y": int(y + h * 0.35),
        "w": int(w * 0.84),
        "h": int(h * 0.52),
    }


def build_positions():
    kf = sorted(KEYFRAMES, key=lambda k: k[0])
    positions = []

    for frame in range(TOTAL_FRAMES):
        prev_kf = kf[0]
        next_kf = kf[-1]

        for i, keyframe in enumerate(kf):
            if keyframe[0] <= frame:
                prev_kf = keyframe
            if keyframe[0] >= frame:
                next_kf = keyframe
                break

        if prev_kf[0] == next_kf[0]:
            _, visible, sx, sy, sw, sh = prev_kf
        else:
            t = (frame - prev_kf[0]) / (next_kf[0] - prev_kf[0])
            visible = prev_kf[1] if t < 0.5 else next_kf[1]
            if prev_kf[1] and next_kf[1]:
                sx = lerp(prev_kf[2], next_kf[2], t)
                sy = lerp(prev_kf[3], next_kf[3], t)
                sw = lerp(prev_kf[4], next_kf[4], t)
                sh = lerp(prev_kf[5], next_kf[5], t)
                visible = True
            elif not prev_kf[1] and not next_kf[1]:
                visible = False
                sx = sy = sw = sh = 0
            elif prev_kf[1] and not next_kf[1]:
                sx, sy, sw, sh = prev_kf[2], prev_kf[3], prev_kf[4], prev_kf[5]
                visible = t < 0.7
            else:
                sx, sy, sw, sh = next_kf[2], next_kf[3], next_kf[4], next_kf[5]
                visible = t > 0.3

        entry = {"frame": frame, "visible": bool(visible)}
        if visible:
            sign = [int(sx), int(sy), int(sw), int(sh)]
            entry["sign"] = {"x": sign[0], "y": sign[1], "w": sign[2], "h": sign[3]}
            entry["text"] = sign_to_text(sign)

        positions.append(entry)

    return positions


def main():
    positions = build_positions()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(positions, f, indent=2)

    visible_count = sum(1 for p in positions if p.get("visible"))
    print(f"Generadas {len(positions)} posiciones ({visible_count} con cartel visible)")
    print(f"Guardado en {OUT_PATH}")


if __name__ == "__main__":
    main()
