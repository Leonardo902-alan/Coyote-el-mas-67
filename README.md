# Cartel del Coyote

Pon texto personalizado en el cartel del Coyote. Cada animación es un clip corto: primero el Coyote saca el cartel y, cuando se queda quieto, aparece tu texto encima.

## Uso en línea (Vercel)

1. Entra a la URL de tu deploy en Vercel
2. Elige **Animación 1–4**, escribe tu texto y reproduce
3. Descarga en **MP4** o **GIF** (se genera en tu navegador, sin servidor)

### Desplegar en Vercel

1. Entra a [vercel.com/dashboard](https://vercel.com/dashboard)
2. **Si ya existe el proyecto** (error *"Project already exists"*):
   - Abre el proyecto **`coyote-el-mas-67`** que ya creaste
   - Ve a **Deployments** → **Redeploy** (o espera el deploy automático al hacer push)
   - **No** vuelvas a pulsar "Add New Project" con el mismo repo
3. **Si es la primera vez**:
   - **Add New Project** → importa [Coyote-el-mas-67](https://github.com/Leonardo902-alan/Coyote-el-mas-67)
   - En **Project Name** puedes usar `coyote-cartel` si el nombre automático ya existe
   - Pulsa **Deploy**
4. Comparte la URL pública (ej. `https://coyote-cartel.vercel.app`)

Solo se despliega la carpeta `public/` (sitio estático). La exportación corre en el navegador del usuario.

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
