import json
import os
from . import run_async_test, create_test_agent, get_flight_booking_spec
from app.agents.parsers.code_generation_parser import CodeGenerationParser
from app.agents.parsers.layer_feedback_parser import LayerFeedbackParser
from app.agents.parsers.overall_feedback_parser import OverallFeedbackParser

def format_json(data: dict, indent: int = 2) -> str:
    """Format JSON data with proper indentation"""
    return json.dumps(data, indent=indent)

def save_agent_output(output_dir: str, agent_name: str, data: dict):
    """Save agent output to a file with proper formatting"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a descriptive filename
    filename = f"{agent_name.lower().replace(' ', '_')}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Save the data
    with open(filepath, "w") as f:
        f.write(format_json(data))
    
    print(f"\n{agent_name} output saved to: {filepath}")

def test_flight_booking_dao():
    """Test generating code for flight booking DAO layer"""
    print("\n=== Starting Flight Booking DAO Test ===")
    
    # Create output directory for this test
    test_name = "flight_booking_dao"
    output_dir = os.path.join("generated_code", test_name)
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nStep 1: Creating test agent...")
    agent = create_test_agent()
    layer_spec = get_flight_booking_spec()
    
    print("\nStep 2: Generating code...")
    result = run_async_test(agent.process({
        "layer_specs": [layer_spec],
        "layer_dependencies": {}
    }))
    
    print("\nStep 3: Validating results...")
    print("\n=== Flight Booking DAO Generation Result ===")
    print(format_json(result))
    
    # Basic assertions
    assert result["status"] == "completed", f"Generation failed: {result.get('error', 'Unknown error')}"
    assert layer_spec["layer_id"] in result["generated_codes"], "Generated code not found for layer"
    
    print("\nStep 4: Saving outputs...")
    # Save master agent output
    save_agent_output(output_dir, "Master Agent", result)
    
    # Save individual agent outputs
    for layer_id, code_info in result["generated_codes"].items():
        print(f"\nSaving outputs for layer: {layer_id}")
        
        # Save code generation output
        code_gen_output = {
            "status": "completed",
            "generated_code": code_info,
            "layer_id": layer_id,
            "metadata": result.get("metadata", {}).get(layer_id, {})
        }
        save_agent_output(output_dir, f"Code Generation - {layer_id}", code_gen_output)
        
        # Save layer feedback output
        layer_feedback = next(
            (f for f in result["feedback"] if f.get("layer_id") == layer_id),
            None
        )
        if layer_feedback:
            save_agent_output(output_dir, f"Layer Feedback - {layer_id}", layer_feedback)
    
    # Save overall feedback output
    overall_feedback = next(
        (f for f in result["feedback"] if f.get("type") == "overall"),
        None
    )
    if overall_feedback:
        save_agent_output(output_dir, "Overall Feedback", overall_feedback)
    
    print("\n=== Test Completed Successfully ===")
    return result

if __name__ == "__main__":
    test_flight_booking_dao() 