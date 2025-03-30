import asyncio
from app.agents.master_agent import MasterAgent
from typing import Dict, Any

def create_test_agent() -> MasterAgent:
    """Create a test instance of the master agent"""
    return MasterAgent()

def run_async_test(coroutine):
    """Run an async test and return the result"""
    return asyncio.run(coroutine)

def get_flight_booking_spec():
    """Get flight booking layer specification"""
    return {
        "layer_id": "flight_booking_dao",
        "language": "python",
        "artifact_type": "dao",
        "functionality_type": "ddb",
        "description": "DynamoDB DAO for flight booking operations",
        "properties": {
            "table_config": {
                "table_name": "flight_bookings",
                "partition_key": "booking_id",
                "sort_key": "created_at"
            },
            "attributes": {
                "booking_id": {
                    "type": "string",
                    "description": "Unique identifier for the booking"
                },
                "created_at": {
                    "type": "string",
                    "description": "Timestamp when the booking was created"
                },
                "user_id": {
                    "type": "string",
                    "description": "ID of the user who made the booking"
                },
                "flight_id": {
                    "type": "string",
                    "description": "ID of the booked flight"
                },
                "status": {
                    "type": "string",
                    "description": "Current status of the booking",
                    "enum": ["pending", "confirmed", "cancelled"]
                },
                "passenger_count": {
                    "type": "integer",
                    "description": "Number of passengers in the booking"
                },
                "total_price": {
                    "type": "number",
                    "description": "Total price of the booking"
                }
            }
        }
    }

def get_flight_booking_service_spec():
    """Get flight booking service layer specification"""
    return {
        "layer_id": "flight_booking_service",
        "language": "python",
        "artifact_type": "service",
        "functionality_type": "business_logic",
        "description": "Service layer for flight booking business logic",
        "properties": {
            "dependencies": ["flight_booking_dao"],
            "methods": [
                {
                    "name": "create_booking",
                    "parameters": [
                        {"name": "user_id", "type": "string"},
                        {"name": "flight_id", "type": "string"},
                        {"name": "passenger_count", "type": "integer"}
                    ],
                    "return_type": "Dict[str, Any]"
                },
                {
                    "name": "get_booking",
                    "parameters": [
                        {"name": "booking_id", "type": "string"}
                    ],
                    "return_type": "Dict[str, Any]"
                },
                {
                    "name": "update_booking_status",
                    "parameters": [
                        {"name": "booking_id", "type": "string"},
                        {"name": "status", "type": "string"}
                    ],
                    "return_type": "Dict[str, Any]"
                }
            ]
        }
    }

def get_flight_booking_controller_spec():
    """Get flight booking controller layer specification"""
    return {
        "layer_id": "flight_booking_controller",
        "language": "python",
        "artifact_type": "controller",
        "functionality_type": "api",
        "description": "API controller for flight booking endpoints",
        "properties": {
            "dependencies": ["flight_booking_service"],
            "endpoints": [
                {
                    "path": "/bookings",
                    "method": "POST",
                    "parameters": [
                        {"name": "user_id", "type": "string"},
                        {"name": "flight_id", "type": "string"},
                        {"name": "passenger_count", "type": "integer"}
                    ],
                    "return_type": "Dict[str, Any]"
                },
                {
                    "path": "/bookings/{booking_id}",
                    "method": "GET",
                    "parameters": [
                        {"name": "booking_id", "type": "string"}
                    ],
                    "return_type": "Dict[str, Any]"
                },
                {
                    "path": "/bookings/{booking_id}/status",
                    "method": "PUT",
                    "parameters": [
                        {"name": "booking_id", "type": "string"},
                        {"name": "status", "type": "string"}
                    ],
                    "return_type": "Dict[str, Any]"
                }
            ]
        }
    }

def get_user_document_spec():
    """Get user document S3 DAO specification"""
    return {
        "layer_id": "user_document_dao",
        "language": "python",
        "artifact_type": "dao",
        "functionality_type": "s3",
        "properties": {
            "bucket_name": "user-documents",
            "file_prefix": "users/",
            "file_extension": ".json",
            "attributes": [
                {"name": "user_id", "type": "string", "required": True},
                {"name": "document_type", "type": "string", "required": True},
                {"name": "file_name", "type": "string", "required": True},
                {"name": "content", "type": "string", "required": True},
                {"name": "created_at", "type": "string", "required": True},
                {"name": "updated_at", "type": "string", "required": True}
            ]
        }
    } 