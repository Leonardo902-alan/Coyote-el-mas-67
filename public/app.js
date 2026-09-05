const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const animTabs = document.getElementById("animTabs");
const signTextInput = document.getElementById("signText");
const textColorSelect = document.getElementById("textColor");
const fontSizeInput = document.getElementById("fontSize");
const playBtn = document.getElementById("playBtn");
const restartBtn = document.getElementById("restartBtn");
const exportMp4Btn = document.getElementById("exportMp4Btn");
const exportGifBtn = document.getElementById("exportGifBtn");
const exportStatus = document.getElementById("exportStatus");
const timeDisplay = document.getElementById("timeDisplay");
const animStatus = document.getElementById("animStatus");

const VIDEO_W = 1280;
const VIDEO_H = 720;
const IS_VERCEL = location.hostname.includes("vercel.app");
const SIGN_FONT = '"Roboto Condensed", "Arial Narrow", sans-serif';

const ANIMATIONS_FALLBACK = [
  { id: 1, file: "coyote1.mp4", label: "Animación 1", totalFrames: 48, fps: 24, textStartFrame: 22, textStartTime: 0.917,
    textBox: { x: 464, y: 413, w: 352, h: 108, centerX: 640, centerY: 467 } },
  { id: 2, file: "coyote2.mp4", label: "Animación 2", totalFrames: 77, fps: 24, textStartFrame: 34, textStartTime: 1.417,
    textBox: { x: 464, y: 415, w: 352, h: 108, centerX: 640, centerY: 469 } },
  { id: 3, file: "coyote3.mp4", label: "Animación 3", totalFrames: 68, fps: 24, textStartFrame: 32, textStartTime: 1.333,
    textBox: { x: 464, y: 415, w: 352, h: 108, centerX: 640, centerY: 469 } },
  { id: 4, file: "coyote4.mp4", label: "Animación 4", totalFrames: 47, fps: 24, textStartFrame: 31, textStartTime: 1.292,
    textBox: { x: 464, y: 415, w: 352, h: 108, centerX: 640, centerY: 469 } },
];

let animations = [];
let currentAnim = null;
let videoReady = false;
let signFontLoaded = false;
let ffmpegInstance = null;

function signFontCss(size) {
  return `italic 700 ${size}px ${SIGN_FONT}`;
}

async function loadSignFont() {
  try {
    const font = new FontFace(
      "Roboto Condensed",
      "url(fonts/RobotoCondensed-BoldItalic.ttf)",
      { weight: "700", style: "italic" }
    );
    await font.load();
    document.fonts.add(font);
    signFontLoaded = true;
  } catch {
    try {
      await document.fonts.load(signFontCss(48));
      signFontLoaded = document.fonts.check(signFontCss(16));
    } catch {
      signFontLoaded = false;
    }
  }
}

async function loadAnimations() {
  try {
    const res = await fetch(`data/animations.json?t=${Date.now()}`);
    if (res.ok) return res.json();
  } catch {}
  return ANIMATIONS_FALLBACK;
}

async function init() {
  try {
    await loadSignFont();
    animations = await loadAnimations();

    animations.forEach((anim) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "anim-tab";
      btn.innerHTML = `<span class="tab-num">${anim.id}</span>${anim.label.replace("Animación ", "")}`;
      btn.dataset.id = anim.id;
      btn.addEventListener("click", () => selectAnim(anim.id));
      animTabs.appendChild(btn);
    });

    selectAnim(1);
    requestAnimationFrame(renderLoop);
  } catch (err) {
    if (animStatus) {
      animStatus.textContent = "Error al cargar la app. Recarga la página.";
      animStatus.className = "export-status error";
    }
    console.error(err);
  }
}

function selectAnim(id) {
  currentAnim = animations.find((a) => a.id === id);
  if (!currentAnim) return;

  document.querySelectorAll(".anim-tab").forEach((tab) => {
    tab.classList.toggle("active", Number(tab.dataset.id) === id);
  });

  videoReady = false;
  video.pause();
  video.src = `video/${currentAnim.file}?v=${Date.now()}`;
  video.load();
  playBtn.textContent = "▶ Reproducir";
  updateAnimStatus();
  drawSignText();
}

function getFps() {
  return currentAnim?.fps || 24;
}

function shouldShowTextAtTime(time) {
  if (!currentAnim) return false;
  const text = signTextInput.value.trim();
  if (!text) return false;
  const startTime = currentAnim.textStartTime ?? currentAnim.textStartFrame / getFps();
  return time >= startTime - 0.04;
}

function shouldShowText() {
  if (!videoReady) return false;
  return shouldShowTextAtTime(video.currentTime);
}

function getScale() {
  const rect = video.getBoundingClientRect();
  const videoAspect = VIDEO_W / VIDEO_H;
  const displayAspect = rect.width / rect.height;

  let drawW, drawH, offX, offY;
  if (displayAspect > videoAspect) {
    drawH = rect.height;
    drawW = drawH * videoAspect;
    offX = (rect.width - drawW) / 2;
    offY = 0;
  } else {
    drawW = rect.width;
    drawH = drawW / videoAspect;
    offX = 0;
    offY = (rect.height - drawH) / 2;
  }
  return { drawW, drawH, offX, offY, scale: drawW / VIDEO_W };
}

function wrapLines(targetCtx, text, maxWidth) {
  const words = text.split(/\s+/).filter(Boolean);
  if (!words.length) return [text];

  const lines = [];
  let current = "";

  for (const word of words) {
    const test = current ? `${current} ${word}` : word;
    if (targetCtx.measureText(test).width <= maxWidth) {
      current = test;
    } else {
      if (current) lines.push(current);
      if (targetCtx.measureText(word).width > maxWidth) {
        let chunk = "";
        for (const char of word) {
          const testChunk = chunk + char;
          if (targetCtx.measureText(testChunk).width <= maxWidth) chunk = testChunk;
          else {
            if (chunk) lines.push(chunk);
            chunk = char;
          }
        }
        current = chunk;
      } else {
        current = word;
      }
    }
  }
  if (current) lines.push(current);
  return lines.length ? lines : [text];
}

function paintSignText(targetCtx, { scale, offsetX, offsetY, showText }) {
  if (!showText || !currentAnim) return;

  const text = signTextInput.value.trim();
  if (!text) return;

  const box = currentAnim.textBox;
  const x = offsetX + box.x * scale;
  const y = offsetY + box.y * scale;
  const w = box.w * scale;
  const h = box.h * scale;
  const cx = offsetX + box.centerX * scale;
  const cy = offsetY + box.centerY * scale;

  let fontSize = Math.max(14, parseInt(fontSizeInput.value, 10) * scale);

  let lines, lineHeight, totalH, widest;
  do {
    targetCtx.font = signFontCss(fontSize);
    lines = wrapLines(targetCtx, text, w * 0.92);
    lineHeight = fontSize * 1.1;
    totalH = lines.length * lineHeight;
    widest = Math.max(...lines.map((l) => targetCtx.measureText(l).width));
    if (widest <= w * 0.92 && totalH <= h * 0.88) break;
    fontSize -= 1;
  } while (fontSize >= 12);

  targetCtx.save();
  targetCtx.beginPath();
  targetCtx.rect(x, y, w, h);
  targetCtx.clip();
  targetCtx.font = signFontCss(fontSize);
  targetCtx.fillStyle = textColorSelect.value;
  targetCtx.textAlign = "center";
  targetCtx.textBaseline = "middle";

  let startY = cy - totalH / 2 + lineHeight / 2;
  for (const line of lines) {
    targetCtx.fillText(line, cx, startY);
    startY += lineHeight;
  }
  targetCtx.restore();
}

function drawSignText() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const { offX, offY, scale } = getScale();
  paintSignText(ctx, {
    scale,
    offsetX: offX,
    offsetY: offY,
    showText: shouldShowText(),
  });
}

function updateAnimStatus() {
  if (!currentAnim || !animStatus) return;
  const t0 = (currentAnim.textStartTime ?? currentAnim.textStartFrame / getFps()).toFixed(1);
  const t1 = (currentAnim.totalFrames / getFps()).toFixed(1);
  animStatus.textContent = `Animación: 0–${t0}s · Texto visible: ${t0}s–${t1}s (igual en las 4)`;
}

function renderLoop() {
  resizeCanvas();
  drawSignText();
  if (video.duration && videoReady) {
    timeDisplay.textContent =
      `${formatTime(video.currentTime)} / ${formatTime(video.duration)}` +
      (shouldShowText() ? " · Texto ON" : " · Texto OFF");
  }
  requestAnimationFrame(renderLoop);
}

function resizeCanvas() {
  const rect = video.getBoundingClientRect();
  if (canvas.width !== rect.width || canvas.height !== rect.height) {
    canvas.width = rect.width;
    canvas.height = rect.height;
  }
}

function formatTime(s) {
  const sec = Math.floor(s || 0);
  return `${Math.floor(sec / 60)}:${(sec % 60).toString().padStart(2, "0")}`;
}

function togglePlay() {
  if (!videoReady) return;
  if (video.paused) {
    video.play();
    playBtn.textContent = "⏸ Pausar";
  } else {
    video.pause();
    playBtn.textContent = "▶ Reproducir";
  }
}

function seekVideo(target, time) {
  return new Promise((resolve) => {
    if (Math.abs(target.currentTime - time) < 0.001) {
      resolve();
      return;
    }
    const onSeeked = () => {
      target.removeEventListener("seeked", onSeeked);
      resolve();
    };
    target.addEventListener("seeked", onSeeked);
    target.currentTime = time;
  });
}

async function getFfmpeg() {
  if (ffmpegInstance) return ffmpegInstance;

  const { FFmpeg } = await import("https://esm.sh/@ffmpeg/ffmpeg@0.12.10");
  const { toBlobURL } = await import("https://esm.sh/@ffmpeg/util@0.12.1");

  const ffmpeg = new FFmpeg();
  const baseURL = "https://cdn.jsdelivr.net/npm/@ffmpeg/core-st@0.12.6/dist/umd";

  ffmpeg.on("log", () => {});

  await ffmpeg.load({
    coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, "text/javascript"),
    wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, "application/wasm"),
  });

  ffmpegInstance = ffmpeg;
  return ffmpeg;
}

async function renderExportFrames(onProgress) {
  const fps = getFps();
  const totalFrames = currentAnim.totalFrames;
  const exportVideo = document.createElement("video");
  exportVideo.src = video.src;
  exportVideo.muted = true;
  exportVideo.playsInline = true;
  exportVideo.preload = "auto";

  await new Promise((resolve, reject) => {
    exportVideo.addEventListener("loadeddata", resolve, { once: true });
    exportVideo.addEventListener("error", reject, { once: true });
    exportVideo.load();
  });

  const offCanvas = document.createElement("canvas");
  offCanvas.width = VIDEO_W;
  offCanvas.height = VIDEO_H;
  const offCtx = offCanvas.getContext("2d");
  const blobs = [];

  for (let i = 0; i < totalFrames; i++) {
    await seekVideo(exportVideo, i / fps);
    offCtx.drawImage(exportVideo, 0, 0, VIDEO_W, VIDEO_H);
    paintSignText(offCtx, {
      scale: 1,
      offsetX: 0,
      offsetY: 0,
      showText: i >= currentAnim.textStartFrame,
    });

    const blob = await new Promise((resolve) => offCanvas.toBlob(resolve, "image/jpeg", 0.9));
    blobs.push(blob);
    onProgress(Math.round(((i + 1) / totalFrames) * 70));
  }

  exportVideo.src = "";
  return { blobs, fps };
}

async function encodeWithFfmpeg(blobs, fps, format, onProgress) {
  const { fetchFile } = await import("https://esm.sh/@ffmpeg/util@0.12.1");
  const ffmpeg = await getFfmpeg();

  for (let i = 0; i < blobs.length; i++) {
    const name = `frame${String(i).padStart(4, "0")}.jpg`;
    await ffmpeg.writeFile(name, await fetchFile(blobs[i]));
  }

  onProgress(85);

  if (format === "mp4") {
    await ffmpeg.exec([
      "-framerate", String(fps),
      "-i", "frame%04d.jpg",
      "-c:v", "libx264",
      "-pix_fmt", "yuv420p",
      "-profile:v", "baseline",
      "-movflags", "+faststart",
      "-an",
      "out.mp4",
    ]);
    onProgress(95);
    const data = await ffmpeg.readFile("out.mp4");
    return new Blob([data.buffer], { type: "video/mp4" });
  }

  await ffmpeg.exec([
    "-framerate", String(fps),
    "-i", "frame%04d.jpg",
    "-vf", "scale=640:360",
    "-y",
    "out.gif",
  ]);
  onProgress(95);
  const data = await ffmpeg.readFile("out.gif");
  return new Blob([data.buffer], { type: "image/gif" });
}

async function exportClipClient(format) {
  const text = signTextInput.value.trim();
  if (!text) {
    exportStatus.textContent = "Escribe un texto primero.";
    exportStatus.className = "export-status error";
    return;
  }
  if (!currentAnim) return;

  exportMp4Btn.disabled = true;
  exportGifBtn.disabled = true;
  exportStatus.textContent = "Preparando exportación...";
  exportStatus.className = "export-status";

  const setProgress = (pct) => {
    exportStatus.textContent =
      format === "gif"
        ? `Generando GIF... ${pct}%`
        : `Generando MP4 (WhatsApp)... ${pct}%`;
  };

  try {
    setProgress(5);
    const { blobs, fps } = await renderExportFrames(setProgress);
    setProgress(75);
    exportStatus.textContent = "Codificando video...";
    const blob = await encodeWithFfmpeg(blobs, fps, format, setProgress);

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `coyote${currentAnim.id}_${text.replace(/\s+/g, "_").slice(0, 15)}.${format}`;
    a.click();
    URL.revokeObjectURL(url);

    exportStatus.textContent =
      format === "mp4" ? "¡MP4 listo para WhatsApp!" : "¡GIF descargado!";
    exportStatus.className = "export-status success";
  } catch (err) {
    exportStatus.textContent = err.message || "Error al exportar. Intenta de nuevo.";
    exportStatus.className = "export-status error";
  } finally {
    exportMp4Btn.disabled = false;
    exportGifBtn.disabled = false;
  }
}

async function exportClipServer(format) {
  const text = signTextInput.value.trim();
  if (!text) {
    exportStatus.textContent = "Escribe un texto primero.";
    exportStatus.className = "export-status error";
    return;
  }
  if (!currentAnim) return;

  exportMp4Btn.disabled = true;
  exportGifBtn.disabled = true;
  exportStatus.textContent =
    format === "gif" ? "Generando GIF..." : "Generando MP4 (compatible WhatsApp)...";
  exportStatus.className = "export-status";

  try {
    const res = await fetch(`/api/export/${format}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        animId: currentAnim.id,
        text,
        color: textColorSelect.value,
        fontSize: parseInt(fontSizeInput.value, 10),
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || "Error al exportar");
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `coyote${currentAnim.id}_${text.replace(/\s+/g, "_").slice(0, 15)}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
    exportStatus.textContent =
      format === "mp4" ? "¡MP4 listo para WhatsApp!" : "¡GIF descargado!";
    exportStatus.className = "export-status success";
  } catch (err) {
    exportStatus.textContent = err.message;
    exportStatus.className = "export-status error";
  } finally {
    exportMp4Btn.disabled = false;
    exportGifBtn.disabled = false;
  }
}

function exportClip(format) {
  if (IS_VERCEL || location.protocol === "file:") {
    return exportClipClient(format);
  }
  return exportClipServer(format);
}

video.addEventListener("loadeddata", () => {
  videoReady = true;
  drawSignText();
});

video.addEventListener("error", () => {
  if (animStatus) {
    animStatus.textContent = "No se pudo cargar el video. Recarga la página.";
    animStatus.className = "export-status error";
  }
});

video.addEventListener("timeupdate", drawSignText);
video.addEventListener("seeked", drawSignText);

video.addEventListener("ended", () => {
  playBtn.textContent = "▶ Reproducir";
});

playBtn.addEventListener("click", togglePlay);
restartBtn.addEventListener("click", () => {
  if (!videoReady) return;
  video.currentTime = 0;
  video.play();
  playBtn.textContent = "⏸ Pausar";
});
exportMp4Btn.addEventListener("click", () => exportClip("mp4"));
exportGifBtn.addEventListener("click", () => exportClip("gif"));
signTextInput.addEventListener("input", drawSignText);
textColorSelect.addEventListener("change", drawSignText);
fontSizeInput.addEventListener("input", () => {
  document.getElementById("fontSizeVal").textContent = fontSizeInput.value;
  drawSignText();
});
window.addEventListener("resize", drawSignText);

init();
