import os
import boto3
from typing import Protocol

class FileStorageProvider(Protocol):
    def upload(self, local_path: str, destination: str) -> None: ...

class S3StorageProvider:
    def __init__(self):
        endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
        # Validación rápida para evitar el error de endpoint
        if not endpoint.startswith("http"):
            endpoint = f"http://{endpoint}"
            
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("MINIO_SECRET_KEY")
        )
        self.bucket = "ekastorage"

    def upload(self, local_path: str, destination: str) -> None:
        with open(local_path, 'rb') as data:
            self.client.upload_fileobj(data, self.bucket, destination)

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)