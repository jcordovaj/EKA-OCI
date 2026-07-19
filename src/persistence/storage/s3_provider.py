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

    def list_objects(self, prefix: str) -> list:
        """Lista objetos en el bucket bajo un prefijo dado."""
        response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]

    def get_hash(self, key: str) -> str:
        """
        Obtiene el ETag (hash MD5) de S3. 
        Nota: Para SHA-256 estricto, habría que descargar el archivo, pero 
        para detección inicial el ETag es suficiente como proxy de cambio.
        """
        response = self.client.head_object(Bucket=self.bucket, Key=key)
        return response['ETag'].strip('"')

    def copy(self, source_key: str, dest_key: str) -> None:
        copy_source = {'Bucket': self.bucket, 'Key': source_key}
        self.client.copy_object(CopySource=copy_source, Bucket=self.bucket, Key=dest_key)

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)
