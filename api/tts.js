const googleTTS = require("google-tts-api");

function getApiKey() {
  return process.env.FISH_AUDIO_API_KEY || process.env.FISH_API_KEY || "";
}

function getDefaultVoiceId() {
  return process.env.FISH_AUDIO_VOICE_ID || "";
}

function getFishModels() {
  const preferred = process.env.FISH_AUDIO_MODEL || "s2-pro";
  const models = [preferred];
  if (preferred !== "s2.1-pro-free") models.push("s2.1-pro-free");
  return models;
}

function parseFishError(status, body) {
  try {
    const data = JSON.parse(body);
    if (status === 401) {
      return "API Key inválida. Crea una en fish.audio/app/api-keys (no uses el ID del modelo).";
    }
    if (status === 402) return "Sin créditos en Fish Audio. Recarga en fish.audio.";
    if (status === 400) return data.message || "ID de voz inválido en Fish Audio.";
    return data.message || `Fish Audio error ${status}`;
  } catch {
    return body.slice(0, 200) || `Fish Audio error ${status}`;
  }
}

async function fishTts(text, referenceId, apiKey) {
  const body = {
    text,
    format: "mp3",
    prosody: { speed: 1, volume: 0, normalize_loudness: true },
  };
  if (referenceId) body.reference_id = referenceId;

  let lastError = "Fish Audio no disponible";

  for (const model of getFishModels()) {
    const response = await fetch("https://api.fish.audio/v1/tts", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        model,
      },
      body: JSON.stringify(body),
    });

    if (response.ok) {
      return Buffer.from(await response.arrayBuffer());
    }

    const errText = await response.text();
    lastError = parseFishError(response.status, errText);
    if (response.status === 401 || response.status === 402) break;
  }

  throw new Error(lastError);
}

async function googleTtsFallback(text) {
  const url = googleTTS.getAudioUrl(text, { lang: "es", slow: false });
  const response = await fetch(url);
  if (!response.ok) throw new Error("TTS de respaldo no disponible");
  return Buffer.from(await response.arrayBuffer());
}

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }

  const text = (req.query.text || "").trim().slice(0, 200);
  const referenceId = (req.query.voice || getDefaultVoiceId()).trim();

  if (!text) {
    res.status(400).json({ error: "Falta el texto" });
    return;
  }

  const apiKey = getApiKey();

  try {
    if (!apiKey) {
      res.status(503).json({
        error: "Falta FISH_AUDIO_API_KEY en Vercel. Obtén una en fish.audio/app/api-keys",
      });
      return;
    }

    const buffer = await fishTts(text, referenceId, apiKey);
    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("Cache-Control", "public, max-age=3600");
    res.send(buffer);
  } catch (err) {
    res.status(500).json({ error: err.message || "Error al generar voz" });
  }
};
