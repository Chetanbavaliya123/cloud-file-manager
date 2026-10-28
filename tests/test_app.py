"""
Unit tests for Cloud File Manager Flask Application.
Tests routing, Supabase mock interactions, upload constraints, and signed URL generation.
"""

import io
import pytest
from unittest.mock import MagicMock, patch
import app as file_manager_app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    file_manager_app.app.config["TESTING"] = True
    file_manager_app.app.config["WTF_CSRF_ENABLED"] = False
    with file_manager_app.app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    """Test that /health returns 200 OK with JSON status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "bucket" in data


def test_index_unconfigured(client):
    """Test that index loads gracefully with a warning when Supabase is not configured."""
    with patch("app.get_supabase_client", return_value=None):
        response = client.get("/")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "Cloud File Manager" in html
        assert "Supabase credentials" in html


def test_index_with_mocked_supabase(client):
    """Test index route listing files and generating signed URLs with both key variants."""
    mock_supabase = MagicMock()
    mock_bucket = MagicMock()
    mock_supabase.storage.from_.return_value = mock_bucket

    # Provide a list with a normal file, a hidden file, and another file with alternate signedUrl key
    mock_bucket.list.return_value = [
        {
            "name": ".emptyFolderPlaceholder",
            "metadata": {"size": 0},
            "created_at": "2026-10-28T10:00:00Z",
        },
        {
            "name": "report.pdf",
            "metadata": {"size": 2048},  # 2 KB
            "created_at": "2026-10-28T10:15:00Z",
        },
        {
            "name": "data file.csv",
            "size": 10240,  # 10 KB
            "created_at": "2026-10-28T10:30:00Z",
        },
    ]

    # Return different signed URL formats to test both signedURL and signedUrl key handling
    def mock_create_signed_url(name, expires_in):
        assert expires_in == 3600
        if name == "report.pdf":
            return {"signedURL": "https://storage.supabase.co/signed/report.pdf?token=123"}
        return {"signedUrl": "https://storage.supabase.co/signed/data%20file.csv?token=456"}

    mock_bucket.create_signed_url.side_effect = mock_create_signed_url

    with patch("app.get_supabase_client", return_value=mock_supabase):
        response = client.get("/")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Verify header & tagline
        assert "Cloud File Manager" in html
        assert "Compute: Render Web Service" in html
        assert "Storage: Supabase Storage" in html
        assert "Files: 2" in html  # .emptyFolderPlaceholder was filtered out

        # Verify files listed
        assert "report.pdf" in html
        assert "data file.csv" in html
        assert ".emptyFolderPlaceholder" not in html

        # Verify sizes in KB
        assert "2.0 KB" in html
        assert "10.0 KB" in html

        # Verify signed download URLs present
        assert "https://storage.supabase.co/signed/report.pdf?token=123" in html
        assert "https://storage.supabase.co/signed/data%20file.csv?token=456" in html


def test_upload_success(client):
    """Test successful file upload with correct MIME type and upsert option."""
    mock_supabase = MagicMock()
    mock_bucket = MagicMock()
    mock_supabase.storage.from_.return_value = mock_bucket

    test_content = b"Cloud Computing Assignment Test Content"
    data = {
        "file": (io.BytesIO(test_content), "cloud_notes.txt", "text/plain")
    }

    with patch("app.get_supabase_client", return_value=mock_supabase):
        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True
        )
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "successfully uploaded" in html

        # Verify mock calls
        mock_bucket.upload.assert_called_once()
        call_args = mock_bucket.upload.call_args
        assert call_args.kwargs["path"] == "cloud_notes.txt"
        assert call_args.kwargs["file"] == test_content
        assert call_args.kwargs["file_options"]["content-type"] == "text/plain"
        assert call_args.kwargs["file_options"]["upsert"] == "true"


def test_upload_no_file(client):
    """Test upload error when no file is submitted."""
    mock_supabase = MagicMock()
    with patch("app.get_supabase_client", return_value=mock_supabase):
        response = client.post("/upload", data={}, follow_redirects=True)
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "No file part provided" in html


def test_upload_supabase_failure_graceful(client):
    """Test that Supabase upload errors are caught gracefully without crashing."""
    mock_supabase = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.upload.side_effect = Exception("Supabase Storage quota exceeded")
    mock_supabase.storage.from_.return_value = mock_bucket

    data = {
        "file": (io.BytesIO(b"Hello Cloud"), "sample.txt", "text/plain")
    }

    with patch("app.get_supabase_client", return_value=mock_supabase):
        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True
        )
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "Upload failed: Supabase Storage quota exceeded" in html


def test_delete_file_success(client):
    """Test deleting a file via route /delete/<path:name>."""
    mock_supabase = MagicMock()
    mock_bucket = MagicMock()
    mock_supabase.storage.from_.return_value = mock_bucket

    with patch("app.get_supabase_client", return_value=mock_supabase):
        response = client.get("/delete/folder/test-document.pdf", follow_redirects=True)
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "deleted successfully" in html
        mock_bucket.remove.assert_called_once_with(["folder/test-document.pdf"])


def test_delete_file_supabase_failure(client):
    """Test that delete errors are caught gracefully without crashing."""
    mock_supabase = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.remove.side_effect = Exception("Storage network timeout")
    mock_supabase.storage.from_.return_value = mock_bucket

    with patch("app.get_supabase_client", return_value=mock_supabase):
        response = client.get("/delete/broken.txt", follow_redirects=True)
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "Failed to delete" in html
        assert "Storage network timeout" in html


def test_upload_file_too_large(client):
    """Test that files exceeding 10 MB trigger the 413 error handler with friendly redirect."""
    oversized_data = {
        "file": (io.BytesIO(b"X" * (10 * 1024 * 1024 + 1024)), "huge_archive.zip")
    }
    with patch("app.get_supabase_client", return_value=MagicMock()):
        response = client.post(
            "/upload",
            data=oversized_data,
            content_type="multipart/form-data",
            follow_redirects=True
        )
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "exceeds the maximum allowed size of 10 MB" in html


def test_view_file_redirect(client):
    """Test that /view/<name> generates an on-demand signed URL and redirects to it."""
    mock_supabase = MagicMock()
    mock_bucket = MagicMock()
    mock_supabase.storage.from_.return_value = mock_bucket
    mock_bucket.create_signed_url.return_value = {
        "signedURL": "https://storage.supabase.co/preview/my_document.pdf?token=secret123"
    }

    with patch("app.get_supabase_client", return_value=mock_supabase):
        response = client.get("/view/my_document.pdf")
        assert response.status_code == 302
        assert "https://storage.supabase.co/preview/my_document.pdf?token=secret123" in response.headers["Location"]



