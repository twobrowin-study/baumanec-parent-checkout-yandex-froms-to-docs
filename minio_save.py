import io
import os
from zipfile import ZIP_DEFLATED, ZipFile

import minio

MINIO_HOST = os.environ["MINIO_HOST"]
MINIO_BUCKET = os.environ["MINIO_BUCKET"]
MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]


def save_to_minio(issue: dict, documents: dict):
    """
    Сохраняет документы в MinIO
    """
    archive_buf = io.BytesIO()
    with ZipFile(archive_buf, "a", ZIP_DEFLATED, False) as archive:
        for filename, document in documents.items():
            archive.writestr(filename, document)
    archive_size = archive_buf.tell()
    archive_buf.seek(0)

    minio_client = minio.Minio(
        MINIO_HOST,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=True,
    )
    minio_client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=issue["minio_archive_name"],
        data=archive_buf,
        length=archive_size,
        content_type="application/zip",
    )
