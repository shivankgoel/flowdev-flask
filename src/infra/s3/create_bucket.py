import logging
from src.infra.config import S3Config
from src.infra.s3.client import S3ClientFactory
from src.infra.s3.manager import S3BucketManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_bucket():
    """Create the S3 bucket if it doesn't exist"""
    try:
        # Initialize S3 client and manager
        config = S3Config()
        client_factory = S3ClientFactory(config)
        manager = S3BucketManager(client_factory)

        # Create the bucket
        logger.info(f"Creating S3 bucket {config.bucket_name}...")
        success = manager.create_bucket()

        if success:
            logger.info(f"Bucket {config.bucket_name} created or already exists")
        else:
            logger.error(f"Failed to create bucket {config.bucket_name}")

        logger.info("Bucket creation process completed")

    except Exception as e:
        logger.error(f"Error creating bucket: {str(e)}")
        raise

if __name__ == "__main__":
    create_bucket() 