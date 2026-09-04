# Cartel del Coyote

Pon texto personalizado en el cartel del Coyote. Cada animación es un clip corto: primero el Coyote saca el cartel y, cuando se queda quieto, aparece tu texto encima.

## Uso en línea (Vercel)

1. Entra a la URL de tu deploy en Vercel
2. Elige **Animación 1–4**, escribe tu texto y reproduce
3. Descarga en **MP4** o **GIF**

### Desplegar en Vercel

1. Sube el repo a GitHub (ya está en [Coyote-el-mas-67](https://github.com/Leonardo902-alan/Coyote-el-mas-67))
2. Entra a [vercel.com](https://vercel.com) → **Add New Project**
3. Importa el repositorio
4. Vercel detecta la config automáticamente — pulsa **Deploy**
5. Comparte la URL pública (ej. `https://tu-proyecto.vercel.app`)

La carpeta `public/` sirve la app y los videos. La exportación MP4/GIF corre en una función serverless (`api/export/`).

> **Nota:** La exportación puede tardar unos segundos. En el plan gratuito de Vercel el límite es ~10 s por función; si falla al exportar, prueba de nuevo o usa el plan Pro (hasta 60 s).

## Uso local

1. `pip install -r requirements.txt` (solo la primera vez)
2. Doble clic en **`iniciar.bat`** o ejecuta `python server.py`
3. Abre **http://127.0.0.1:5000**
4. Elige animación, escribe tu texto y descarga MP4/GIF

## Las 4 animaciones

| Clip | Qué hace |
|------|----------|
| Animación 1 | Saca el cartel (~1 s), luego se queda quieto |
| Animación 2 | Guarda y vuelve a sacar el cartel |
| Animación 3 | Saca el cartel con temblor y se queda quieto |
| Animación 4 | Otra variación de sacar el cartel |

El texto **solo aparece cuando el cartel deja de moverse**, fijo encima del cartel.

## Videos fuente

Coloca tus clips en `public/video/` como `coyote1.mp4` … `coyote4.mp4`.  
Si los cambias, ejecuta:

```
python scripts/analyze_animations.py
```
