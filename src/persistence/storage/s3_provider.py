import boto3
from core.settings import settings # Importación centralizada

class S3StorageProvider:
    def __init__(self):
        # Usamos settings en lugar de os.getenv
        endpoint = settings.minio_endpoint
        
        if not endpoint.startswith("http"):
            endpoint = f"http://{endpoint}"

        self.client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key
        )
        self.bucket = settings.minio_bucket # Uso del parámetro centralizado

    def upload(self, local_path: str, destination: str) -> None:
        with open(local_path, 'rb') as data:
            self.client.upload_fileobj(data, self.bucket, destination)

    def list_objects(self, prefix: str) -> list:
        response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]

    def get_hash(self, key: str) -> str:
        response = self.client.head_object(Bucket=self.bucket, Key=key)
        return response['ETag'].strip('"')

    def copy(self, source_key: str, dest_key: str) -> None:
        copy_source = {'Bucket': self.bucket, 'Key': source_key}
        self.client.copy_object(CopySource=copy_source, Bucket=self.bucket, Key=dest_key)

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)
        