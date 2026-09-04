"""Utilidades para texto multilínea en el cartel."""


def wrap_words(text: str, measure_width, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return [text]

    lines: list[str] = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        if measure_width(test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            if measure_width(word) > max_width:
                chunk = ""
                for char in word:
                    test_chunk = chunk + char
                    if measure_width(test_chunk) <= max_width:
                        chunk = test_chunk
                    else:
                        if chunk:
                            lines.append(chunk)
                        chunk = char
                current = chunk
            else:
                current = word

    if current:
        lines.append(current)

    return lines if lines else [text]


def fit_multiline(font_loader, text: str, max_w: float, max_h: float, base_size: int):
    """Devuelve (font, lines, line_height) ajustados al recuadro."""
    font_size = max(16, base_size)
    font = font_loader(font_size)

    def measure(text_line: str) -> float:
        bbox = font.getbbox(text_line) if hasattr(font, "getbbox") else (0, 0, len(text_line) * font_size * 0.5, font_size)
        return bbox[2] - bbox[0]

    while font_size >= 14:
        font = font_loader(font_size)
        lines = wrap_words(text, measure, max_w * 0.92)
        line_height = font_size * 1.12
        total_h = len(lines) * line_height
        widest = max(measure(line) for line in lines)
        if widest <= max_w * 0.92 and total_h <= max_h * 0.88:
            return font, lines, line_height
        font_size -= 1

    font = font_loader(max(14, font_size))
    lines = wrap_words(text, measure, max_w * 0.92)
    return font, lines, max(14, font_size) * 1.12
