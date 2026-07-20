import boto3
from core.settings import settings

class S3StorageProvider:
    def __init__(self, custom_settings=None):
        self.settings = custom_settings or settings
        endpoint = self.settings.STORAGE_ENDPOINT
        
        if not endpoint.startswith("http"):
            endpoint = f"http://{endpoint}"

        self.client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=self.settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=self.settings.STORAGE_SECRET_KEY
        )
        self.bucket = self.settings.BUCKET_NAME

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
        