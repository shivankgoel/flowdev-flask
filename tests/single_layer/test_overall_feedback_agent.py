import json
import os
from . import run_async_test, get_flight_booking_spec
from app.agents.overall_feedback_agent import OverallFeedbackAgent

def format_json(data: dict, indent: int = 2) -> str:
    """Format JSON data with proper indentation"""
    return json.dumps(data, indent=indent)

def save_agent_output(output_dir: str, data: dict):
    """Save agent output to a file with proper formatting"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "overall_feedback_output.json")
    with open(filepath, "w") as f:
        f.write(format_json(data))
    print(f"\nOverall feedback output saved to: {filepath}")

def test_overall_feedback_agent():
    """Test the overall feedback agent in isolation"""
    print("\n=== Starting Overall Feedback Agent Test ===")
    
    # Create output directory for this test
    test_name = "overall_feedback_agent"
    output_dir = os.path.join("generated_code", test_name)
    
    print("\nStep 1: Creating overall feedback agent...")
    agent = OverallFeedbackAgent()
    layer_spec = get_flight_booking_spec()
    
    # Generate some sample code and feedback for testing
    sample_code = """
class FlightBookingDynamoDBDAO(DynamoDBDAO):
    def create_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return super().create_item(item)
        
    def get_item(self, key: Dict[str, Any]) -> Dict[str, Any]:
        return super().get_item(key)
    """
    
    sample_feedback = {
        "type": "layer",
        "layer_id": "flight_booking_dao",
        "needs_update": False,
        "feedback": {
            "scores": {
                "code_quality": 85,
                "error_handling": 80,
                "documentation": 75,
                "testability": 90
            },
            "issues": [],
            "suggestions": [],
            "critical_issues": [],
            "summary": "Code looks good overall"
        }
    }
    
    print("\nStep 2: Getting overall feedback...")
    result = run_async_test(agent.process(layer_spec, sample_code, [sample_feedback]))
    
    print("\nStep 3: Validating results...")
    print("\n=== Overall Feedback Result ===")
    print(format_json(result))
    
    # Basic assertions
    assert result["status"] == "completed", f"Feedback failed: {result.get('error', 'Unknown error')}"
    assert "feedback" in result, "Feedback not found in result"
    assert "needs_update" in result, "Needs update flag not found in result"
    assert "layers_to_update" in result, "Layers to update not found in result"
    
    print("\nStep 4: Saving output...")
    save_agent_output(output_dir, result)
    
    print("\n=== Test Completed Successfully ===")
    return result

if __name__ == "__main__":
    test_overall_feedback_agent() 