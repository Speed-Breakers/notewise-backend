import io
from typing import BinaryIO
import boto3
from botocore.client import BaseClient
from fastapi import UploadFile
from env import DO_SPACES_ENDPOINT, DO_SPACES_KEY, DO_SPACES_PLACE, DO_SPACES_SECRET
from pdf import PDFDocument

client: BaseClient = boto3.client(
    "s3",
    endpoint_url=DO_SPACES_ENDPOINT,
    region_name=DO_SPACES_PLACE,
    aws_access_key_id=DO_SPACES_KEY,
    aws_secret_access_key=DO_SPACES_SECRET,
)


def upload_file(file: io.BytesIO, pdf: PDFDocument):
    print("Uploading file")
    client.put_object(
        Bucket="notewise",
        Key=f"{pdf.pdf_id}/{pdf.name}",
        Body=file,
        ContentType="application/pdf",
        ACL="public-read",
    )
