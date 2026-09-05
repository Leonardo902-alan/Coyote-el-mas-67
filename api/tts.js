const googleTTS = require("google-tts-api");

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }

  const text = (req.query.text || "").trim().slice(0, 200);
  if (!text) {
    res.status(400).json({ error: "Falta el texto" });
    return;
  }

  try {
    const url = googleTTS.getAudioUrl(text, { lang: "es", slow: false });
    const response = await fetch(url);
    if (!response.ok) throw new Error("TTS no disponible");

    const buffer = Buffer.from(await response.arrayBuffer());
    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("Cache-Control", "public, max-age=3600");
    res.send(buffer);
  } catch (err) {
    res.status(500).json({ error: err.message || "Error al generar voz" });
  }
};
