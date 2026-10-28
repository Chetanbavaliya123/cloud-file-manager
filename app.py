"""
Cloud File Manager
------------------
A production-ready college assignment project for Cloud Computing.
Demonstrates:
  - Compute: Render Web Service (PaaS)
  - Storage: Supabase Storage (Private Bucket via Service-Role Key)
  - Access Control: Signed URLs (time-limited access without public exposure)
  - Resource Management: 10 MB request limit enforcement, error boundaries

Author: Chetan Bavaliya
College: GMIU
Subject: Cloud Computing
"""

import os
import mimetypes
import logging
from urllib.parse import quote, unquote
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort,
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Secret key for secure session handling and flash alerts
app.secret_key = os.environ.get(
    "SECRET_KEY", "cloud-file-manager-default-dev-secret-key-change-in-prod"
)

# Enforce strict 10 MB upload limit at Flask request engine level
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 Megabytes

# Cloud Configuration from Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
BUCKET_NAME = os.environ.get("BUCKET_NAME", "uploads").strip().strip("'\"")
PORT = int(os.environ.get("PORT", 5000))

# Setup application logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloud-file-manager")


def get_clean_supabase_url(raw_url: str) -> str:
    """
    Sanitizes SUPABASE_URL to scheme://netloc (e.g. https://xyz.supabase.co).
    Removes accidental paths like '/rest/v1' or trailing slashes that can cause
    PGRST125 PostgREST routing conflicts with Supabase Storage.
    """
    if not raw_url:
        return ""
    from urllib.parse import urlparse
    clean = raw_url.strip().strip("'\"")
    parsed = urlparse(clean)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return clean.rstrip("/")


def get_supabase_client():
    """
    Initializes and returns a Supabase client.
    Returns None if environment variables are not configured.
    """
    clean_url = get_clean_supabase_url(SUPABASE_URL)
    clean_key = SUPABASE_KEY.strip().strip("'\"")
    if not clean_url or not clean_key:
        logger.warning("Supabase credentials not configured in environment.")
        return None
    try:
        from supabase import create_client
        return create_client(clean_url, clean_key)
    except Exception as exc:
        logger.error(f"Error initializing Supabase client: {exc}")
        return None


def get_file_icon(filename: str) -> str:
    """Helper to return an emoji icon based on file extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]:
        return "🖼️"
    if ext in [".pdf"]:
        return "📕"
    if ext in [".zip", ".rar", ".7z", ".tar", ".gz"]:
        return "📦"
    if ext in [".txt", ".md", ".log", ".rtf"]:
        return "📝"
    if ext in [".py", ".js", ".html", ".css", ".json", ".yaml", ".yml", ".sql"]:
        return "💻"
    if ext in [".mp3", ".wav", ".ogg"]:
        return "🎵"
    if ext in [".mp4", ".mov", ".avi", ".mkv"]:
        return "🎬"
    if ext in [".csv", ".xlsx", ".xls"]:
        return "📊"
    return "📄"


def extract_signed_url(response) -> str | None:
    """
    Extracts the signed URL string from a Supabase Storage response.
    Handles both 'signedURL' and 'signedUrl' key variants across SDK versions.
    """
    if not response:
        return None
    if isinstance(response, dict):
        return response.get("signedURL") or response.get("signedUrl")
    return getattr(response, "signedURL", None) or getattr(response, "signedUrl", None)


@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    """Gracefully handles upload files exceeding 10 MB limit."""
    flash("Upload failed: File exceeds the maximum allowed size of 10 MB.", "error")
    return redirect(url_for("index"))


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint for Render monitoring and uptime checks.
    Returns JSON status.
    """
    clean_url = get_clean_supabase_url(SUPABASE_URL)
    return jsonify({
        "status": "ok",
        "service": "cloud-file-manager",
        "bucket": BUCKET_NAME,
        "configured": bool(clean_url and SUPABASE_KEY)
    }), 200


@app.route("/", methods=["GET"])
def index():
    """
    Home page: Lists all files in the Supabase Storage bucket,
    generates time-limited signed download URLs (3600 seconds),
    and displays upload form.
    """
    files = []
    error_banner = None

    supabase = get_supabase_client()
    if not supabase:
        error_banner = (
            "Supabase credentials (SUPABASE_URL, SUPABASE_KEY) are not set. "
            "Please configure your environment variables to enable cloud storage."
        )
        return render_template(
            "index.html",
            files=[],
            bucket_name=BUCKET_NAME,
            error_banner=error_banner
        )

    try:
        # Retrieve list of objects from bucket
        bucket = supabase.storage.from_(BUCKET_NAME)
        raw_items = bucket.list()

        for item in raw_items:
            name = item.get("name", "")
            # Skip hidden files and placeholder objects
            if not name or name.startswith("."):
                continue

            # Calculate size in KB
            metadata = item.get("metadata") or {}
            raw_size = metadata.get("size") if isinstance(metadata, dict) else None
            if raw_size is None:
                raw_size = item.get("size", 0)

            try:
                size_kb = round(float(raw_size) / 1024.0, 1)
            except (ValueError, TypeError):
                size_kb = 0.0

            # Generate signed URL valid for 3600 seconds (1 hour)
            download_url = None
            try:
                signed_res = bucket.create_signed_url(name, 3600)
                download_url = extract_signed_url(signed_res)
            except Exception as sign_err:
                logger.warning(f"Could not generate signed URL for {name}: {sign_err}")

            # Format created/updated timestamp
            created_at_raw = item.get("created_at") or item.get("updated_at")
            formatted_date = "Recently"
            if created_at_raw:
                try:
                    dt = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
                    formatted_date = dt.strftime("%b %d, %Y %H:%M")
                except Exception:
                    formatted_date = str(created_at_raw)[:16]

            files.append({
                "name": name,
                "encoded_name": quote(name),
                "size_kb": size_kb,
                "created_at": formatted_date,
                "download_url": download_url,
                "icon": get_file_icon(name),
            })

    except Exception as exc:
        logger.error(f"Error listing bucket files: {exc}", exc_info=True)
        flash(f"Cloud Storage Error: Unable to list files ({str(exc)})", "error")

    return render_template(
        "index.html",
        files=files,
        bucket_name=BUCKET_NAME,
        error_banner=error_banner
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Uploads a file to Supabase Storage bucket.
    Enforces secure filename, sets content-type, and enables upsert=True.
    """
    supabase = get_supabase_client()
    if not supabase:
        flash("Cannot upload: Supabase credentials are not configured.", "error")
        return redirect(url_for("index"))

    if "file" not in request.files:
        flash("No file part provided in upload request.", "warning")
        return redirect(url_for("index"))

    file = request.files["file"]
    if not file or file.filename.strip() == "":
        flash("Please select a file to upload.", "warning")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    if not filename:
        flash("Invalid file name. Please rename the file and try again.", "error")
        return redirect(url_for("index"))

    try:
        # Determine MIME type
        content_type = file.content_type
        if not content_type or content_type == "application/octet-stream":
            guessed, _ = mimetypes.guess_type(filename)
            content_type = guessed or "application/octet-stream"

        file_bytes = file.read()

        # Upload file directly to Supabase storage bucket
        bucket = supabase.storage.from_(BUCKET_NAME)
        file_options = {
            "content-type": content_type,
            "upsert": "true",
        }

        bucket.upload(
            path=filename,
            file=file_bytes,
            file_options=file_options
        )

        flash(f"File '{filename}' successfully uploaded to '{BUCKET_NAME}' bucket!", "success")
    except Exception as exc:
        logger.error(f"Failed to upload file '{filename}': {exc}", exc_info=True)
        flash(f"Upload failed: {str(exc)}", "error")

    return redirect(url_for("index"))


@app.route("/delete/<path:name>", methods=["GET", "POST"])
def delete_file(name):
    """
    Deletes a file from the Supabase Storage bucket.
    Decodes URL path safely and catches any remote exceptions.
    """
    supabase = get_supabase_client()
    if not supabase:
        flash("Cannot delete: Supabase credentials are not configured.", "error")
        return redirect(url_for("index"))

    decoded_name = unquote(name)

    try:
        bucket = supabase.storage.from_(BUCKET_NAME)
        bucket.remove([decoded_name])
        flash(f"File '{decoded_name}' deleted successfully.", "success")
    except Exception as exc:
        logger.error(f"Failed to delete file '{decoded_name}': {exc}", exc_info=True)
        flash(f"Failed to delete '{decoded_name}': {str(exc)}", "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    # Local development server only
    # In production (Render), Gunicorn is used: gunicorn app:app
    logger.info(f"Starting local Flask server on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=True)
