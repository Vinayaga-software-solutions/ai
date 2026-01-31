"""
Document Storage Module
Saves ingested documents to local folder (dev) or GCS bucket (prod).
Backend is configured via STORAGE_BACKEND (local | gcs).
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import logging
import shutil
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)


class DocumentStorage(ABC):
    """Abstract base for document storage backends."""

    @abstractmethod
    def save_content(self, content: bytes, filename: str, doc_id: Optional[str] = None) -> str:
        """Save raw content. Returns the storage path or blob name."""
        pass

    @abstractmethod
    def save_file(self, file_path: str, doc_id: Optional[str] = None) -> str:
        """Save/copy an existing file. Returns the storage path or blob name."""
        pass


class LocalDocumentStorage(DocumentStorage):
    """Saves documents to a local directory."""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local document storage: {self.base_path.absolute()}")

    def _target_path(self, filename: str, doc_id: Optional[str] = None) -> Path:
        safe_name = Path(filename).name
        if doc_id:
            stem, suffix = (safe_name.rsplit(".", 1) + [""])[:2]
            if suffix:
                safe_name = f"{stem}_{doc_id}.{suffix}"
            else:
                safe_name = f"{stem}_{doc_id}"
        return self.base_path / safe_name

    def save_content(self, content: bytes, filename: str, doc_id: Optional[str] = None) -> str:
        path = self._target_path(filename, doc_id)
        path.write_bytes(content)
        logger.info(f"Saved document to local: {path}")
        return str(path)

    def save_file(self, file_path: str, doc_id: Optional[str] = None) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        target = self._target_path(path.name, doc_id)
        shutil.copy2(path, target)
        logger.info(f"Copied document to local: {target}")
        return str(target)


class GCSDocumentStorage(DocumentStorage):
    """Saves documents to a Google Cloud Storage bucket."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ):
        self.bucket_name = bucket_name or settings.GCS_BUCKET_NAME
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME must be set when STORAGE_BACKEND=gcs")
        self._client = None
        self._credentials_path = credentials_path or settings.GCS_CREDENTIALS_PATH

    def _get_client(self):
        if self._client is None:
            try:
                from google.cloud import storage
            except ImportError:
                raise ImportError(
                    "google-cloud-storage is required for GCS. Install with: pip install google-cloud-storage"
                )
            if self._credentials_path:
                self._client = storage.Client.from_service_account_json(self._credentials_path)
            else:
                self._client = storage.Client()
        return self._client

    def _blob_name(self, filename: str, doc_id: Optional[str] = None) -> str:
        safe_name = Path(filename).name
        if doc_id:
            stem, suffix = (safe_name.rsplit(".", 1) + [""])[:2]
            if suffix:
                safe_name = f"{stem}_{doc_id}.{suffix}"
            else:
                safe_name = f"{stem}_{doc_id}"
        prefix = datetime.utcnow().strftime("%Y/%m/%d")
        return f"documents/{prefix}/{safe_name}"

    def save_content(self, content: bytes, filename: str, doc_id: Optional[str] = None) -> str:
        client = self._get_client()
        bucket = client.bucket(self.bucket_name)
        blob_name = self._blob_name(filename, doc_id)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(content, content_type="application/octet-stream")
        logger.info(f"Saved document to GCS: gs://{self.bucket_name}/{blob_name}")
        return f"gs://{self.bucket_name}/{blob_name}"

    def save_file(self, file_path: str, doc_id: Optional[str] = None) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        client = self._get_client()
        bucket = client.bucket(self.bucket_name)
        blob_name = self._blob_name(path.name, doc_id)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(path))
        logger.info(f"Uploaded document to GCS: gs://{self.bucket_name}/{blob_name}")
        return f"gs://{self.bucket_name}/{blob_name}"


def get_document_storage() -> DocumentStorage:
    """Return the configured storage backend (local or GCS)."""
    backend = (settings.STORAGE_BACKEND or "local").strip().lower()
    if backend == "gcs":
        return GCSDocumentStorage()
    return LocalDocumentStorage()
