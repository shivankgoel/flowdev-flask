import asyncio
import json
from app import create_app
from app.agents.chatgpt_agent import ChatGPTAgent

async def test_single_layer():
    """Test generating code for a single layer"""
    agent = ChatGPTAgent()
    
    # Test data for flight booking DAO
    layer_spec = {
        "parent_layer_ids": [],
        "layer_id": 1,
        "language": "python3.7",
        "artifact_type": "class",
        "functionality_type": "ddb_dao_layer",
        "properties": {
            "flight_booking_id": "string (pk)",
            "timestamp": "timestamp (sk)",
            "userid": "string",
            "username": "string",
            "flight_status": "string",
            "from": "string",
            "to": "string",
            "flight_time": "timestamp"
        },
        "description": "manages crudl; get and store flight booking details"
    }
    
    result = await agent.process({"layer_spec": layer_spec})
    print("\n=== Single Layer Generation Result ===")
    print(json.dumps(result, indent=2))

async def test_multi_layer():
    """Test generating code for multiple layers with dependencies"""
    agent = ChatGPTAgent()
    
    # Test data for multiple layers
    layers = [
        {
            "parent_layer_ids": [],
            "layer_id": 1,
            "language": "python3.7",
            "artifact_type": "class",
            "functionality_type": "ddb_dao_layer",
            "properties": {
                "flight_booking_id": "string (pk)",
                "timestamp": "timestamp (sk)",
                "userid": "string",
                "username": "string",
                "flight_status": "string",
                "from": "string",
                "to": "string",
                "flight_time": "timestamp"
            },
            "description": "manages crudl; get and store flight booking details"
        },
        {
            "parent_layer_ids": [],
            "layer_id": 2,
            "language": "python3.7",
            "artifact_type": "class",
            "functionality_type": "s3_dao_layer",
            "properties": {
                "userid": "string",
                "goverment_issued_id": "image"
            },
            "description": "manages crudl; get and store govt id image"
        },
        {
            "parent_layer_ids": [1, 2],
            "layer_id": 3,
            "language": "python3.7",
            "artifact_type": "class",
            "functionality_type": "dao_layer",
            "description": "manager crudl;"
        }
    ]
    
    # Add all layers to the manager
    for layer_spec in layers:
        agent.layer_manager.add_layer(layer_spec)
    
    # Get the order of layers to process
    layer_order = agent.get_layer_order()
    print("\n=== Layer Processing Order ===")
    print(layer_order)
    
    # Generate code for each layer in order
    results = {}
    for layer_id in layer_order:
        layer_spec = agent.layer_manager.get_layer_spec(layer_id)
        result = await agent.process({"layer_spec": layer_spec})
        results[layer_id] = result
        print(f"\n=== Generated Code for Layer {layer_id} ===")
        print(result["generated_code"][layer_id])
    
    return results

async def main():
    """Main test function"""
    print("Starting code generation tests...")
    
    # Test single layer generation
    await test_single_layer()
    
    # Test multi-layer generation
    print("\nTesting multi-layer generation...")
    results = await test_multi_layer()
    
    print("\nTests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 