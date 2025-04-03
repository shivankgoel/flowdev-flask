from typing import List
from botocore.exceptions import ClientError
from src.infra.dynamodb.client import DynamoDBClientFactory
from src.infra.dynamodb.tables import (
    CANVAS_TABLE,
    NODES_TABLE,
    EDGES_TABLE,
    CHAT_THREADS_TABLE
)

class DynamoDBTableManager:
    def __init__(self, client_factory: DynamoDBClientFactory):
        self.client = client_factory.client
        self.resource = client_factory.resource

    def create_table(self, table_definition) -> bool:
        """Create a DynamoDB table with the given definition"""
        try:
            create_table_params = {
                'TableName': table_definition.table_name,
                'KeySchema': [
                    {'AttributeName': table_definition.partition_key, 'KeyType': 'HASH'},
                    {'AttributeName': table_definition.sort_key, 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': table_definition.attributes,
                'BillingMode': table_definition.billing_mode
            }

            # Only add ProvisionedThroughput if using PROVISIONED billing mode
            if table_definition.billing_mode == 'PROVISIONED':
                create_table_params['ProvisionedThroughput'] = {
                    'ReadCapacityUnits': table_definition.read_capacity_units,
                    'WriteCapacityUnits': table_definition.write_capacity_units
                }

            self.client.create_table(**create_table_params)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                # Table already exists
                return True
            raise

    def create_all_tables(self) -> List[bool]:
        """Create all required tables"""
        results = []
        for table in [CANVAS_TABLE, NODES_TABLE, EDGES_TABLE, CHAT_THREADS_TABLE]:
            results.append(self.create_table(table))
        return results

    def delete_table(self, table_name: str) -> bool:
        """Delete a DynamoDB table"""
        try:
            self.client.delete_table(TableName=table_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Table doesn't exist
                return True
            raise

    def delete_all_tables(self) -> List[bool]:
        """Delete all tables"""
        results = []
        for table in [CANVAS_TABLE, NODES_TABLE, EDGES_TABLE, CHAT_THREADS_TABLE]:
            results.append(self.delete_table(table.table_name))
        return results 