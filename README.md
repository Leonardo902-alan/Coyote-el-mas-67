# Cartel del Coyote

Pon texto personalizado en el cartel del Coyote. Cada animación es un clip corto: primero el Coyote saca el cartel y, cuando se queda quieto, aparece tu texto encima.

## Uso rápido

1. `pip install -r requirements.txt` (solo la primera vez)
2. Doble clic en **`iniciar.bat`**
3. Abre **http://127.0.0.1:5000**
4. Elige **Animación 1–4**, escribe tu texto y reproduce
5. Descarga en **MP4** o **GIF**

## Las 4 animaciones

| Clip | Qué hace |
|------|----------|
| Animación 1 | Saca el cartel (~1 s), luego se queda quieto |
| Animación 2 | Guarda y vuelve a sacar el cartel |
| Animación 3 | Saca el cartel con temblor y se queda quieto |
| Animación 4 | Otra variante de sacar el cartel |

El texto **solo aparece cuando el cartel deja de moverse**, fijo encima del cartel.

## Videos fuente

Coloca tus clips en `video/` como `coyote1.mp4` … `coyote4.mp4`.  
Si los cambias, ejecuta:

```
python scripts/analyze_animations.py
```
