# 🚀 Deployment Details Specification

This document details the complete cloud architecture, infrastructure configurations, security model, and resource management policies for the **Cloud File Manager** application.

---

## 📊 Cloud Deployment Summary Table

| Attribute | Specification / Configuration Details |
| :--- | :--- |
| **Cloud Platform** | Multi-Cloud Architecture: **Render.com** (Compute) + **Supabase Cloud** (Storage) |
| **Compute Service** | **Render Web Service** (Platform-as-a-Service / PaaS) |
| **Storage Service** | **Supabase Storage** (Backend-as-a-Service / BaaS; S3-compatible Object Storage) |
| **Compute Region** | `Singapore` (`ap-southeast-1` equivalent on AWS/GCP underlying infra) |
| **Access Control** | <ul><li>**Private Bucket**: Bucket `uploads` has public access disabled; no unauthenticated reads.</li><li>**Server-Side Secret Key**: Flask backend uses `service_role` key to authenticate securely with Supabase.</li><li>**Signed URLs**: End-users download objects through cryptographic time-limited URLs valid for **3600 seconds (1 hour)**.</li></ul> |
| **Secrets Management** | Zero secrets in source control. Environment variables injected via Render Dashboard (`sync: false` in `render.yaml`) and local `.env` (git-ignored). |
| **Deployment Method** | Continuous Deployment (CI/CD) via GitHub Integration: Render automatically detects pushes to `main` branch, executes build commands, and triggers zero-downtime deployment. |
| **Web Server** | **Gunicorn 26.x** (WSGI HTTP Server for UNIX) serving Flask application: `gunicorn app:app` |
| **Public URL** | `https://cloud-file-manager-xxxx.onrender.com` *(Updated upon deployment)* |
| **HTTPS / TLS** | Automatically provisioned and renewed SSL/TLS certificates via **Let's Encrypt**, managed natively by Render Edge router. |
| **Resource Management** | <ul><li>**Upload Limit**: 10 MB per-file maximum, strictly enforced in Flask (`MAX_CONTENT_LENGTH = 10 * 1024 * 1024`) and browser JavaScript before transmission.</li><li>**Auto-Sleep Policy**: Render Free instance sleeps after 15 minutes of inactivity; spins up automatically upon incoming HTTP request.</li><li>**Monitoring**: Live CPU/Memory telemetry available under Render **Metrics** tab; application access logs under **Logs** tab.</li><li>**Storage Quota Monitoring**: Available via Supabase **Project Settings > Usage & Storage** (1 GB limit).</li></ul> |
| **Total Infrastructure Cost** | **$0.00 / Month** (100% Free Tier, zero credit card requirement) |

---

## 🔒 Security Architecture & Access Control Flow

```text
[End User]
    │
    ▼ (1. HTTPS Request)
[Render Edge Load Balancer] (TLS Termination, DDoS Protection)
    │
    ▼ (2. Reverse Proxy)
[Gunicorn + Flask Engine] ─── (Reads SUPABASE_KEY from Secure Env)
    │
    ├── (3. Authenticated API Call via Service-Role Key) ──► [Supabase API Gateway]
    │                                                               │
    │                                                               ▼
    │                                                    [Private S3 Bucket 'uploads']
    │
    ◄── (4. Returns Ephemeral Signed URL: Expires in 3600s) ────────┘
    │
    ▼ (5. HTTP Response with Download Link)
[End User Browser]
    │
    ▼ (6. Direct Fetch via Signed URL)
[Supabase Storage CDN]
```

### Key Security Safeguards
1. **Private by Default**: Storage bucket is marked private so raw bucket URLs (`https://xyz.supabase.co/storage/v1/object/public/...`) return `403 Forbidden`.
2. **Server-Side Secret Isolation**: The `service_role` key remains strictly isolated on the server runtime and is never leaked to client HTML or JavaScript.
3. **MIME-Type & Filename Sanitization**: Filenames are sanitized via Werkzeug's `secure_filename()` to neutralize path traversal attacks (`../../etc/passwd`). Content-type headers are explicitly enforced.
4. **Error Masking**: Database or network connection errors from Supabase are trapped by application error handlers, preventing stack traces or database schema leakage.

---

## 📈 Resource Management & Monitoring Checklist

1. **Memory & CPU Monitoring**:
   - Check Render Dashboard -> **cloud-file-manager** -> **Metrics** tab.
   - Verify memory usage remains well within the 512 MB Free Tier ceiling.

2. **Application Log Auditing**:
   - Check Render Dashboard -> **Logs** tab for incoming HTTP status codes (200, 302, 413) and worker status.

3. **Storage Usage Auditing**:
   - Check Supabase Dashboard -> **Storage** -> `uploads` bucket to view stored object count and cumulative bytes.
   - Check Supabase Dashboard -> **Settings** -> **Usage** to ensure bandwidth and object limits remain under free tier quotas.
