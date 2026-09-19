# -*- coding: utf-8 -*-
# 2462 L2C 免费替身链: OpenAI兼容STT(Vosk) + 本地免费数据层(tasks/contacts/gmail/calendar)
# 单进程, 0 外部付费依赖, port 8765
import json, re, subprocess, tempfile, os, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from vosk import Model, KaldiRecognizer, SetLogLevel

MODEL_DIR = r"C:\Users\Administrator\.easyclaw\workspace\n8n-lesson-crew\state\factory\vosk-model\vosk-model-small-cn-0.22"
SetLogLevel(-1)
print("[free-stack] loading vosk model...", flush=True)
model = Model(MODEL_DIR)
print("[free-stack] vosk ready", flush=True)

DATA = {
    "tasks":    {"tasks": [{"title": "reply-to-customer-email", "due": "today"}, {"title": "submit-weekly-report", "due": "today"}]},
    "contacts": {"contacts": [{"name": "Zhang-san", "email": "zhang.san@example.com", "phone": "13800001111"}, {"name": "Li-si", "email": "li.si@example.com", "phone": "13900002222"}]},
    "gmail":    {"messages": [
        {"from": "boss@corp.example", "date": "today 09:00", "subject": "年度报表评审", "snippet": "明天上午10点会议室A评审年度报表"},
        {"from": "promo@mall.example", "date": "today 08:30", "subject": "限时大促5折起", "snippet": "全场五折"}]},
    "calendar": {"events": [{"summary": "weekly-product-sync", "start": "14:00"}, {"summary": "1on1 with Zhang-san", "start": "16:30"}]},
}

def transcribe(raw: bytes, fname: str) -> str:
    ext = os.path.splitext(fname)[1] or ".ogg"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as fi:
        fi.write(raw); src = fi.name
    wav = src + ".wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "wav", wav], check=True)
    wf = open(wav, "rb")
    wf.read(44)  # skip header? use proper wav reader instead
    wf.close()
    import wave
    w = wave.open(wav, "rb")
    rec = KaldiRecognizer(model, w.getframerate())
    rec.SetWords(False)
    text = []
    while True:
        data = w.readframes(4000)
        if len(data) == 0: break
        if rec.AcceptWaveform(data):
            text.append(json.loads(rec.Result()).get("text", ""))
    text.append(json.loads(rec.FinalResult()).get("text", ""))
    w.close()
    os.remove(src); os.remove(wav)
    return " ".join(t for t in text if t).strip()

def parse_multipart(body: bytes, ctype: str):
    m = re.search(r"boundary=([^\s;]+)", ctype)
    if not m: return None, {}
    boundary = m.group(1).strip('"').encode()
    parts = body.split(b"--" + boundary)
    file = None; fields = {}
    for p in parts:
        if b"\r\n\r\n" not in p: continue
        head, _, content = p.partition(b"\r\n\r\n")
        content = content.rstrip(b"\r\n")
        hm = re.search(rb'Content-Disposition: form-data; name="([^"]+)"(?:; filename="([^"]*)")?', head)
        if not hm: continue
        name = hm.group(1).decode()
        if hm.group(2):
            file = (hm.group(2).decode(), content)
        else:
            fields[name] = content.decode("utf-8", "ignore")
    return file, fields

class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        key = self.path.strip("/").split("?")[0]
        if key == "health": return self._json({"ok": True, "vosk": True})
        if key in DATA: return self._json(DATA[key])
        return self._json({"error": "not found"}, 404)
    def do_POST(self):
        key = self.path.strip("/").split("?")[0]
        if key == "v1/audio/transcriptions":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            file, fields = parse_multipart(body, self.headers.get("Content-Type", ""))
            if not file: return self._json({"error": "no file"}, 400)
            fname, raw = file
            try:
                text = transcribe(raw, fname)
            except Exception as e:
                return self._json({"error": f"stt failed: {e}"}, 500)
            print(f"[free-stack] STT {fname} -> {text}", flush=True)
            return self._json({"text": text})
        return self._json({"error": "not found"}, 404)

if __name__ == "__main__":
    port = 8766
    HTTPServer(("127.0.0.1", port), H).serve_forever()