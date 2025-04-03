import logging
from src.infra.config import DynamoDBConfig
from src.infra.dynamodb.client import DynamoDBClientFactory
from src.infra.dynamodb.manager import DynamoDBTableManager
from src.infra.dynamodb.tables import (
    CANVAS_TABLE,
    NODES_TABLE,
    EDGES_TABLE,
    CHAT_THREADS_TABLE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all DynamoDB tables if they don't exist"""
    try:
        # Initialize DynamoDB client and manager
        config = DynamoDBConfig()
        client_factory = DynamoDBClientFactory(config)
        manager = DynamoDBTableManager(client_factory)

        # Create all tables
        logger.info("Creating DynamoDB tables...")
        results = manager.create_all_tables()

        # Log results
        tables = [
            CANVAS_TABLE.table_name,
            NODES_TABLE.table_name,
            EDGES_TABLE.table_name,
            CHAT_THREADS_TABLE.table_name
        ]
        
        for table_name, success in zip(tables, results):
            if success:
                logger.info(f"Table {table_name} created or already exists")
            else:
                logger.error(f"Failed to create table {table_name}")

        logger.info("Table creation process completed")

    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

if __name__ == "__main__":
    create_tables() 