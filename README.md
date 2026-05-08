# 📥 SocialDL — Descargador de Videos

Descarga videos de **más de 1.000 plataformas** (YouTube, Instagram, TikTok, Twitter/X, Facebook, Twitch, Vimeo, Reddit y muchas más) directamente en **MP4** desde tu navegador.

![SocialDL preview](https://raw.githubusercontent.com/tu-usuario/social-dl/main/preview.png)

## ✨ Características

- 🎬 Descarga videos en formato **MP4**
- 📊 Selección de calidad: Máxima, 1080p, 720p, 480p
- 👁️ Vista previa del video antes de descargar (título, miniatura, duración)
- 📡 Barra de progreso en tiempo real con velocidad y ETA
- 🌐 Interfaz web accesible desde cualquier dispositivo en la red local
- 🔒 Sin anuncios, sin rastreo — 100% local
- 🧹 Limpieza automática de archivos (elimina tras 1 hora)

## 🛠️ Requisitos

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/download.html) instalado y en el PATH

## 🚀 Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/social-dl.git
cd social-dl
```

### 2. Crea un entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Instala ffmpeg

- **Windows**: Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y añádelo al PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 5. Inicia el servidor

```bash
python app.py
```

### 6. Abre el navegador

```
http://localhost:5000
```

## 📱 Uso desde móvil / otros dispositivos

Si quieres acceder desde otro dispositivo en tu red local (móvil, tablet…):

1. Obtén la IP de tu ordenador:
   - Windows: `ipconfig`
   - macOS/Linux: `ifconfig` o `ip a`
2. Abre en el otro dispositivo: `http://TU_IP:5000`

## 🐳 Uso con Docker

```bash
docker build -t social-dl .
docker run -p 5000:5000 -v $(pwd)/downloads:/app/downloads social-dl
```

## 🔧 Plataformas soportadas

SocialDL usa **yt-dlp** bajo el capó, que soporta más de 1.000 sitios:

| Plataforma | Estado |
|---|---|
| YouTube | ✅ |
| Instagram (Reels, posts) | ✅ |
| TikTok | ✅ |
| Twitter / X | ✅ |
| Facebook | ✅ |
| Twitch (clips y VODs) | ✅ |
| Vimeo | ✅ |
| Reddit | ✅ |
| Dailymotion | ✅ |
| Y muchos más... | ✅ |

Ver lista completa en [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## ⚠️ Aviso legal

Este software es únicamente para **uso personal y educativo**. Respeta siempre los derechos de autor y los términos de servicio de cada plataforma. No descargues contenido protegido sin permiso del autor.

## 📄 Licencia

MIT License — libre para uso personal.
