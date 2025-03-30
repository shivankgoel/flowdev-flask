from typing import Dict, Any, List
from tests import run_async_test, create_test_agent

def get_flight_booking_three_layers():
    """Get flight booking three layers specification"""
    return [
        {
            "layer_id": "flight_booking_dao",
            "language": "python",
            "artifact_type": "dao",
            "functionality_type": "ddb",
            "properties": {
                "table_name": "flight_bookings",
                "partition_key": "booking_id",
                "sort_key": "user_id",
                "attributes": [
                    {"name": "booking_id", "type": "string", "required": True},
                    {"name": "user_id", "type": "string", "required": True},
                    {"name": "flight_number", "type": "string", "required": True},
                    {"name": "departure_date", "type": "string", "required": True},
                    {"name": "status", "type": "string", "required": True},
                    {"name": "created_at", "type": "string", "required": True},
                    {"name": "updated_at", "type": "string", "required": True}
                ]
            }
        },
        {
            "layer_id": "flight_booking_service",
            "language": "python",
            "artifact_type": "service",
            "functionality_type": "business_logic",
            "properties": {
                "parent_layer_ids": ["flight_booking_dao"],
                "methods": [
                    {
                        "name": "create_booking",
                        "parameters": [
                            {"name": "user_id", "type": "string", "required": True},
                            {"name": "flight_number", "type": "string", "required": True},
                            {"name": "departure_date", "type": "string", "required": True}
                        ],
                        "return_type": "Dict[str, Any]"
                    },
                    {
                        "name": "get_booking",
                        "parameters": [
                            {"name": "booking_id", "type": "string", "required": True},
                            {"name": "user_id", "type": "string", "required": True}
                        ],
                        "return_type": "Dict[str, Any]"
                    },
                    {
                        "name": "update_booking_status",
                        "parameters": [
                            {"name": "booking_id", "type": "string", "required": True},
                            {"name": "user_id", "type": "string", "required": True},
                            {"name": "status", "type": "string", "required": True}
                        ],
                        "return_type": "Dict[str, Any]"
                    }
                ]
            }
        },
        {
            "layer_id": "flight_booking_controller",
            "language": "python",
            "artifact_type": "controller",
            "functionality_type": "api",
            "properties": {
                "parent_layer_ids": ["flight_booking_service"],
                "endpoints": [
                    {
                        "path": "/bookings",
                        "method": "POST",
                        "parameters": [
                            {"name": "user_id", "type": "string", "required": True},
                            {"name": "flight_number", "type": "string", "required": True},
                            {"name": "departure_date", "type": "string", "required": True}
                        ],
                        "return_type": "Dict[str, Any]"
                    },
                    {
                        "path": "/bookings/{booking_id}",
                        "method": "GET",
                        "parameters": [
                            {"name": "booking_id", "type": "string", "required": True},
                            {"name": "user_id", "type": "string", "required": True}
                        ],
                        "return_type": "Dict[str, Any]"
                    },
                    {
                        "path": "/bookings/{booking_id}/status",
                        "method": "PUT",
                        "parameters": [
                            {"name": "booking_id", "type": "string", "required": True},
                            {"name": "user_id", "type": "string", "required": True},
                            {"name": "status", "type": "string", "required": True}
                        ],
                        "return_type": "Dict[str, Any]"
                    }
                ]
            }
        }
    ] 