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

let animations = [];
let currentAnim = null;
let videoReady = false;
let bangersLoaded = false;

async function loadBangersFont() {
  try {
    const font = new FontFace("Bangers", "url(/fonts/Bangers-Regular.ttf)");
    await font.load();
    document.fonts.add(font);
    bangersLoaded = true;
  } catch {
    bangersLoaded = false;
  }
}

async function init() {
  await loadBangersFont();
  const res = await fetch("/data/animations.json?t=" + Date.now());
  animations = await res.json();

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
}

function selectAnim(id) {
  currentAnim = animations.find((a) => a.id === id);
  if (!currentAnim) return;

  document.querySelectorAll(".anim-tab").forEach((tab) => {
    tab.classList.toggle("active", Number(tab.dataset.id) === id);
  });

  videoReady = false;
  video.pause();
  video.src = `/video/${currentAnim.file}?v=${Date.now()}`;
  video.load();
  playBtn.textContent = "▶ Reproducir";
  updateAnimStatus();
  drawSignText();
}

function getFps() {
  return currentAnim?.fps || 24;
}

function shouldShowText() {
  if (!currentAnim || !videoReady) return false;
  const text = signTextInput.value.trim();
  if (!text) return false;

  const startTime = currentAnim.textStartTime ?? currentAnim.textStartFrame / getFps();
  return video.currentTime >= startTime - 0.04;
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

function wrapLines(ctx, text, maxWidth) {
  const words = text.split(/\s+/).filter(Boolean);
  if (!words.length) return [text];

  const lines = [];
  let current = "";

  for (const word of words) {
    const test = current ? `${current} ${word}` : word;
    if (ctx.measureText(test).width <= maxWidth) {
      current = test;
    } else {
      if (current) lines.push(current);
      if (ctx.measureText(word).width > maxWidth) {
        let chunk = "";
        for (const char of word) {
          const testChunk = chunk + char;
          if (ctx.measureText(testChunk).width <= maxWidth) chunk = testChunk;
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

function drawSignText() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (!shouldShowText()) return;

  const text = signTextInput.value.trim();
  const box = currentAnim.textBox;
  const { offX, offY, scale } = getScale();

  const x = offX + box.x * scale;
  const y = offY + box.y * scale;
  const w = box.w * scale;
  const h = box.h * scale;
  const cx = offX + box.centerX * scale;
  const cy = offY + box.centerY * scale;

  let fontSize = Math.max(14, parseInt(fontSizeInput.value, 10) * scale);
  const fontFamily = bangersLoaded ? "Bangers" : "cursive";

  let lines, lineHeight, totalH, widest;
  do {
    ctx.font = `${fontSize}px "${fontFamily}", cursive`;
    lines = wrapLines(ctx, text, w * 0.92);
    lineHeight = fontSize * 1.12;
    totalH = lines.length * lineHeight;
    widest = Math.max(...lines.map((l) => ctx.measureText(l).width));
    if (widest <= w * 0.92 && totalH <= h * 0.88) break;
    fontSize -= 1;
  } while (fontSize >= 12);

  ctx.save();
  ctx.beginPath();
  ctx.rect(x, y, w, h);
  ctx.clip();
  ctx.font = `${fontSize}px "${fontFamily}", cursive`;
  ctx.fillStyle = textColorSelect.value;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.strokeStyle = "rgba(0,0,0,0.12)";
  ctx.lineWidth = Math.max(1, fontSize * 0.04);
  ctx.lineJoin = "round";

  let startY = cy - totalH / 2 + lineHeight / 2;
  for (const line of lines) {
    ctx.strokeText(line, cx, startY);
    ctx.fillText(line, cx, startY);
    startY += lineHeight;
  }
  ctx.restore();
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

async function exportClip(format) {
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

video.addEventListener("loadeddata", () => {
  videoReady = true;
  drawSignText();
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
