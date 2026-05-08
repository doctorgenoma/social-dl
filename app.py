import os
import re
import uuid
import threading
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import yt_dlp

app = Flask(__name__)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Track download jobs: {job_id: {status, progress, filename, error}}
jobs = {}

# Auto-cleanup: remove files older than 1 hour
def cleanup_old_files():
    while True:
        time.sleep(300)
        now = time.time()
        for f in DOWNLOAD_DIR.iterdir():
            if f.is_file() and (now - f.stat().st_mtime) > 3600:
                try:
                    f.unlink()
                except Exception:
                    pass
        # Clean old job entries
        to_delete = [jid for jid, j in jobs.items()
                     if j.get("done") and (now - j.get("ts", now)) > 3600]
        for jid in to_delete:
            jobs.pop(jid, None)

threading.Thread(target=cleanup_old_files, daemon=True).start()


def make_progress_hook(job_id):
    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            percent = int(downloaded / total * 100) if total else 0
            speed = d.get("_speed_str", "")
            eta = d.get("_eta_str", "")
            jobs[job_id]["progress"] = percent
            jobs[job_id]["speed"] = speed
            jobs[job_id]["eta"] = eta
            jobs[job_id]["status"] = "downloading"
        elif d["status"] == "finished":
            jobs[job_id]["status"] = "processing"
            jobs[job_id]["progress"] = 99
    return hook


def run_download(job_id, url, quality):
    output_template = str(DOWNLOAD_DIR / f"{job_id}_%(title).80s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "progress_hooks": [make_progress_hook(job_id)],
        "noplaylist": True,
		"cookiefile": "cookies/cookies.txt",
        "quiet": True,
        "no_warnings": True,
    }

    if quality == "best":
        ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    elif quality == "1080":
        ydl_opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]"
    elif quality == "720":
        ydl_opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]"
    elif quality == "480":
        ydl_opts["format"] = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]"
    else:
        ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

    # Ensure MP4 output via ffmpeg post-processing
    ydl_opts["merge_output_format"] = "mp4"
    ydl_opts["postprocessors"] = [{
        "key": "FFmpegVideoConvertor",
        "preferedformat": "mp4",
    }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")

        # Find the output file
        found = None
        for f in DOWNLOAD_DIR.iterdir():
            if f.name.startswith(job_id) and f.suffix == ".mp4":
                found = f
                break
        if not found:
            # Try any file with job_id prefix
            candidates = list(DOWNLOAD_DIR.glob(f"{job_id}_*"))
            if candidates:
                found = candidates[0]

        if found:
            jobs[job_id]["status"] = "done"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["filename"] = found.name
            jobs[job_id]["title"] = title
            jobs[job_id]["done"] = True
            jobs[job_id]["ts"] = time.time()
        else:
            raise FileNotFoundError("Output file not found after download.")

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["done"] = True
        jobs[job_id]["ts"] = time.time()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.get_json()
    url = (data or {}).get("url", "").strip()
    if not url:
        return jsonify({"error": "URL requerida"}), 400
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "cookiefile": "cookies/cookies.txt",}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({
            "title": info.get("title", ""),
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", ""),
            "platform": info.get("extractor_key", ""),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.get_json()
    url = (data or {}).get("url", "").strip()
    quality = (data or {}).get("quality", "best")
    if not url:
        return jsonify({"error": "URL requerida"}), 400

    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {"status": "queued", "progress": 0, "speed": "", "eta": ""}

    thread = threading.Thread(target=run_download, args=(job_id, url, quality), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job no encontrado"}), 404
    return jsonify(job)


@app.route("/api/file/<job_id>")
def download_file(job_id):
    job = jobs.get(job_id)
    if not job or job.get("status") != "done":
        return jsonify({"error": "Archivo no disponible"}), 404
    filename = job.get("filename")
    if not filename:
        return jsonify({"error": "Archivo no encontrado"}), 404
    filepath = DOWNLOAD_DIR / filename
    if not filepath.exists():
        return jsonify({"error": "Archivo eliminado"}), 404
    # Clean title for download name
    safe_title = re.sub(r'[^\w\s\-.]', '', job.get("title", "video"))[:80]
    download_name = f"{safe_title}.mp4" if safe_title else filename
    return send_file(str(filepath), as_attachment=True, download_name=download_name)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
