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

> **Si sigue fallando el build:** en Vercel → **Settings** → **General** → **Framework Preset** → elige **Other** → guarda y haz **Redeploy**.

Solo se despliega la carpeta `public/` (sitio estático). La exportación corre en el navegador del usuario.

### Voz IA con Fish Audio (gratis con tu token)

1. En Vercel → tu proyecto → **Settings** → **Environment Variables**
2. Añade:
   - **Name:** `FISH_AUDIO_API_KEY`
   - **Value:** tu token de [fish.audio](https://fish.audio)
3. Guarda y haz **Redeploy**
4. En la app activa **Voz IA (Fish Audio)** y elige un estilo de voz

Para una voz concreta de Fish Studio, copia su **ID** en fish.audio y pégalo en *ID de voz personalizada*.

**Local:** copia `.env.example` a `.env` y pon tu token ahí (nunca lo subas a GitHub).

## Uso local

1. `pip install -r requirements-local.txt` (solo la primera vez)
2. El archivo **`.env`** ya trae tu token de Fish Audio (no se sube a GitHub)
3. Doble clic en **`iniciar.bat`** o ejecuta `python server.py`
4. Abre **http://127.0.0.1:5000**
5. Activa **Voz IA (Fish Audio)**, elige voz y descarga MP4/GIF

Si falta `.env`, copia `.env.example` y pon tu token:

```
FISH_AUDIO_API_KEY=tu_token
FISH_AUDIO_MODEL=s2-pro
```

### Vercel (mismo token, plan Pro)

Ejecuta **`configurar-vercel.bat`** para ver los pasos, o en Vercel añade:

| Variable | Valor |
|----------|--------|
| `FISH_AUDIO_API_KEY` | tu token de fish.audio |
| `FISH_AUDIO_MODEL` | `s2-pro` |

Luego **Redeploy**.

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
