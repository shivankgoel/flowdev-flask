from typing import List
from botocore.exceptions import ClientError
from src.infra.s3.client import S3ClientFactory
from src.infra.config import S3Config

class S3BucketManager:
    def __init__(self, client_factory: S3ClientFactory):
        self.client = client_factory.client
        self.resource = client_factory.resource
        self.config = client_factory.config

    def create_bucket(self) -> bool:
        """Create the S3 bucket if it doesn't exist"""
        try:
            # Check if bucket exists
            self.client.head_bucket(Bucket=self.config.bucket_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, create it
                try:
                    # us-east-1 is the default region and doesn't need a LocationConstraint
                    create_bucket_params = {'Bucket': self.config.bucket_name}
                    if self.config.region != 'us-east-1':
                        create_bucket_params['CreateBucketConfiguration'] = {
                            'LocationConstraint': self.config.region
                        }
                    
                    self.client.create_bucket(**create_bucket_params)
                    return True
                except ClientError as e:
                    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                        return True
                    raise
            raise

    def delete_bucket(self) -> bool:
        """Delete the S3 bucket and all its contents"""
        try:
            # First, delete all objects in the bucket
            bucket = self.resource.Bucket(self.config.bucket_name)
            bucket.objects.all().delete()
            
            # Then delete the bucket
            self.client.delete_bucket(Bucket=self.config.bucket_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                return True
            raise

    def get_object_key(self, prefix: str, id: str) -> str:
        """Generate an S3 object key based on prefix and ID"""
        return f"{prefix}{id}"

    def get_canvas_key(self, canvas_id: str) -> str:
        """Get the S3 key for a canvas"""
        return self.get_object_key(self.config.canvas_prefix, canvas_id)

    def get_node_key(self, node_id: str) -> str:
        """Get the S3 key for a node"""
        return self.get_object_key(self.config.node_prefix, node_id)

    def get_edge_key(self, edge_id: str) -> str:
        """Get the S3 key for an edge"""
        return self.get_object_key(self.config.edge_prefix, edge_id)

    def get_chat_key(self, chat_id: str) -> str:
        """Get the S3 key for a chat"""
        return self.get_object_key(self.config.chat_prefix, chat_id) 