# 📸 Screenshot Submission Checklist

This guide provides exact step-by-step instructions for capturing the 5 required screenshots for your **Cloud Computing College Assignment Submission (GMIU Portal)**.

---

## 📋 Summary of Required Screenshots

| # | Screenshot Name | File Name Recommendation | What Must Be Visible |
| :-: | :--- | :--- | :--- |
| **1** | **Live Web Application** | `screenshot_1_live_app.png` | Browser address bar showing `https://...onrender.com`, green "Cloud File Manager" header, tagline with file count, uploaded files list, download and delete buttons. |
| **2** | **Supabase Storage Bucket** | `screenshot_2_supabase_bucket.png` | Supabase dashboard at **Storage > Buckets > uploads**, showing the uploaded test files with size, file names, and bucket marked as Private. |
| **3** | **Render Service Dashboard** | `screenshot_3_render_live.png` | Render dashboard showing service name `cloud-file-manager`, green **"Live"** status pill, Region `Singapore`, and Instance Type `Free`. |
| **4** | **Render Logs / Metrics Tab** | `screenshot_4_render_logs.png` | Render **Logs** or **Metrics** tab showing Gunicorn worker startup, successful HTTP 200 GET requests, or CPU/Memory utilization charts. |
| **5** | **GitHub Repository** | `screenshot_5_github_repo.png` | GitHub repository page showing repo name `cloud-file-manager`, commits, project files, and README preview. |

---

## 🔍 Detailed Capture Instructions

### Screenshot 1: Running App with URL Bar and Uploaded Files
1. Open Google Chrome or Microsoft Edge.
2. Navigate to your live Render public URL (e.g. `https://cloud-file-manager-xxxx.onrender.com`).
3. Ensure at least 1 or 2 test files (e.g., `assignment_doc.pdf` or `sample_image.png`) have been uploaded using the upload form.
4. **Key Elements to Capture**:
   - The browser URL address bar displaying `https://...onrender.com`
   - The app title "☁️ Cloud File Manager"
   - The tagline showing `Compute: Render Web Service | Storage: Supabase Storage | Bucket: uploads | Files: X`
   - The table listing the uploaded files with Download and Delete action buttons.
5. Save as `docs/screenshots/screenshot_1_live_app.png`.

---

### Screenshot 2: Supabase Storage Bucket
1. Log in to [https://supabase.com/dashboard](https://supabase.com/dashboard).
2. Open your project -> Click on **Storage** in the left sidebar.
3. Click on the `uploads` bucket.
4. **Key Elements to Capture**:
   - The Supabase top-left project title
   - Storage sidebar with `uploads` bucket selected
   - The file listing inside `uploads` showing the uploaded files
   - Notice the "Private bucket" badge or setting indicator.
5. Save as `docs/screenshots/screenshot_2_supabase_bucket.png`.

---

### Screenshot 3: Render Dashboard (Live Status & Region)
1. Log in to [https://dashboard.render.com](https://dashboard.render.com).
2. Click on the `cloud-file-manager` Web Service.
3. Open the **Overview** or **Settings** page.
4. **Key Elements to Capture**:
   - The service name `cloud-file-manager`
   - The green `Live` status badge
   - The public `.onrender.com` URL link
   - The **Region** showing `Singapore`
   - The **Instance Type** showing `Free`
5. Save as `docs/screenshots/screenshot_3_render_live.png`.

---

### Screenshot 4: Render Metrics or Logs Tab
1. Inside the Render dashboard for `cloud-file-manager`:
2. Click on the **Logs** tab (or **Metrics** tab).
3. **Key Elements to Capture**:
   - The log stream showing Gunicorn booting up (`Booting worker with pid...`)
   - Incoming HTTP requests (e.g., `GET / 200`, `POST /upload 302`, `GET /health 200`)
   - Or CPU / RAM telemetry graph if on the Metrics tab.
5. Save as `docs/screenshots/screenshot_4_render_logs.png`.

---

### Screenshot 5: GitHub Repository
1. Open your browser and navigate to `https://github.com/Chetanbavaliya123/cloud-file-manager`.
2. **Key Elements to Capture**:
   - The repo title `Chetanbavaliya123/cloud-file-manager`
   - The repository file list (`app.py`, `render.yaml`, `requirements.txt`, `README.md`, etc.)
   - The commit history count
   - The README banner preview at the bottom.
5. Save as `docs/screenshots/screenshot_5_github_repo.png`.

---

## 📁 Recommended Directory Structure for Screenshots

```text
docs/
└── screenshots/
    ├── screenshot_1_live_app.png
    ├── screenshot_2_supabase_bucket.png
    ├── screenshot_3_render_live.png
    ├── screenshot_4_render_logs.png
    └── screenshot_5_github_repo.png
```

Once all 5 screenshots are saved in this folder, you can export `docs/REPORT.md` to PDF for your final submission on the GMIU portal!
