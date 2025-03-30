import json
import os
from . import run_async_test, get_flight_booking_spec
from app.agents.layer_feedback_agent import LayerFeedbackAgent

def format_json(data: dict, indent: int = 2) -> str:
    """Format JSON data with proper indentation"""
    return json.dumps(data, indent=indent)

def save_agent_output(output_dir: str, data: dict):
    """Save agent output to a file with proper formatting"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "layer_feedback_output.json")
    with open(filepath, "w") as f:
        f.write(format_json(data))
    print(f"\nLayer feedback output saved to: {filepath}")

def test_layer_feedback_agent():
    """Test the layer feedback agent in isolation"""
    print("\n=== Starting Layer Feedback Agent Test ===")
    
    # Create output directory for this test
    test_name = "layer_feedback_agent"
    output_dir = os.path.join("generated_code", test_name)
    
    print("\nStep 1: Creating layer feedback agent...")
    agent = LayerFeedbackAgent()
    layer_spec = get_flight_booking_spec()
    
    # Generate some sample code for testing
    sample_code = """
class FlightBookingDynamoDBDAO(DynamoDBDAO):
    def create_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return super().create_item(item)
        
    def get_item(self, key: Dict[str, Any]) -> Dict[str, Any]:
        return super().get_item(key)
    """
    
    print("\nStep 2: Getting feedback...")
    result = run_async_test(agent.process(layer_spec, sample_code))
    
    print("\nStep 3: Validating results...")
    print("\n=== Layer Feedback Result ===")
    print(format_json(result))
    
    # Basic assertions
    assert result["status"] == "completed", f"Feedback failed: {result.get('error', 'Unknown error')}"
    assert "feedback" in result, "Feedback not found in result"
    assert "needs_update" in result, "Needs update flag not found in result"
    
    print("\nStep 4: Saving output...")
    save_agent_output(output_dir, result)
    
    print("\n=== Test Completed Successfully ===")
    return result

if __name__ == "__main__":
    test_layer_feedback_agent() 