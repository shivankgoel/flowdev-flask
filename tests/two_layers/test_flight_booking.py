import json
from . import run_async_test, create_test_agent, get_flight_booking_layers

def test_flight_booking_layers():
    """Test generating code for flight booking layers"""
    agent = create_test_agent()
    layers = get_flight_booking_layers()
    
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
        result = run_async_test(agent.process({"layer_spec": layer_spec}))
        results[layer_id] = result
        print(f"\n=== Generated Code for Layer {layer_id} ===")
        print(result["generated_code"][layer_id])
    
    # Basic assertions
    assert len(results) == 2
    assert all(result["status"] == "completed" for result in results.values())
    assert layer_order == [1, 2]  # Verify correct order
    
    return results

if __name__ == "__main__":
    test_flight_booking_layers() 