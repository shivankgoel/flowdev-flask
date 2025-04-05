import boto3
from typing import Optional
from src.infra.db.config import db_settings
from src.infra.dynamodb.tables import CANVAS_TABLE, NODES_TABLE, EDGES_TABLE, CHAT_THREADS_TABLE

class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    _dynamodb = None
    _dynamodb_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connections."""
        self._dynamodb = boto3.resource(
            'dynamodb',
            region_name=db_settings.DYNAMODB_REGION,
            endpoint_url=db_settings.DYNAMODB_ENDPOINT_URL,
            aws_access_key_id=db_settings.DYNAMODB_ACCESS_KEY_ID,
            aws_secret_access_key=db_settings.DYNAMODB_SECRET_ACCESS_KEY
        )
        
        self._dynamodb_client = boto3.client(
            'dynamodb',
            region_name=db_settings.DYNAMODB_REGION,
            endpoint_url=db_settings.DYNAMODB_ENDPOINT_URL,
            aws_access_key_id=db_settings.DYNAMODB_ACCESS_KEY_ID,
            aws_secret_access_key=db_settings.DYNAMODB_SECRET_ACCESS_KEY
        )

    @property
    def dynamodb(self):
        """Get DynamoDB resource."""
        return self._dynamodb

    @property
    def dynamodb_client(self):
        """Get DynamoDB client."""
        return self._dynamodb_client

    def create_tables(self):
        """Create all required DynamoDB tables if they don't exist."""
        tables = [CANVAS_TABLE, NODES_TABLE, EDGES_TABLE, CHAT_THREADS_TABLE]
        
        for table in tables:
            try:
                self._create_table(table)
            except Exception as e:
                print(f"Error creating table {table.table_name}: {str(e)}")

    def _create_table(self, table_definition):
        """Create a single DynamoDB table."""
        try:
            # Check if table exists
            self._dynamodb_client.describe_table(TableName=table_definition.table_name)
            print(f"Table {table_definition.table_name} already exists")
        except self._dynamodb_client.exceptions.ResourceNotFoundException:
            # Create table if it doesn't exist
            create_params = {
                'TableName': table_definition.table_name,
                'KeySchema': [
                    {'AttributeName': table_definition.partition_key, 'KeyType': 'HASH'},
                    {'AttributeName': table_definition.sort_key, 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': table_definition.attributes,
                'BillingMode': table_definition.billing_mode
            }

            if table_definition.billing_mode == 'PROVISIONED':
                create_params['ProvisionedThroughput'] = {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }

            self._dynamodb_client.create_table(**create_params)
            print(f"Created table {table_definition.table_name}")

# Global database manager instance
db_manager = DatabaseManager() 