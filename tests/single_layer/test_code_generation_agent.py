import json
import os
from . import run_async_test, get_flight_booking_spec
from app.agents.code_generation_agent import CodeGenerationAgent

def format_json(data: dict, indent: int = 2) -> str:
    """Format JSON data with proper indentation"""
    return json.dumps(data, indent=indent)

def parse_generated_code(result: dict) -> dict:
    """Parse the generated code JSON string into a dictionary"""
    # Extract the JSON string from the result
    json_str = result["generated_code"]
    
    # Remove markdown code block markers if present
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    
    # Parse the JSON string
    parsed_data = json.loads(json_str)
    return parsed_data

def save_agent_output(output_dir: str, data: dict, layer_id: str):
    """Save agent output to files with proper formatting"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse the generated code
    parsed_data = parse_generated_code(data)
    
    # Save metadata to JSON file
    metadata = {
        "status": parsed_data["status"],
        "metadata": parsed_data["metadata"],
        "generated_code": {
            "language": parsed_data["generated_code"]["language"],
            "imports": parsed_data["generated_code"]["imports"],
            "dependencies": parsed_data["generated_code"]["dependencies"],
            "notes": parsed_data["generated_code"]["notes"]
        }
    }
    json_filepath = os.path.join(output_dir, "code_generation_output.json")
    with open(json_filepath, "w") as f:
        f.write(format_json(metadata))
    print(f"\nCode generation metadata saved to: {json_filepath}")
    
    # Save code to Python file
    code_filepath = os.path.join(output_dir, f"{layer_id}.py")
    with open(code_filepath, "w") as f:
        f.write(parsed_data["generated_code"]["code"])
    print(f"Generated code saved to: {code_filepath}")

def test_code_generation_agent():
    """Test the code generation agent in isolation"""
    print("\n=== Starting Code Generation Agent Test ===")
    
    # Create output directory for this test
    test_name = "code_generation_agent"
    output_dir = os.path.join("generated_code", test_name)
    
    print("\nStep 1: Creating code generation agent...")
    agent = CodeGenerationAgent()
    layer_spec = get_flight_booking_spec()
    
    # Prepare input data in the expected format
    input_data = {
        "layer_spec": layer_spec,
        "parent_code": None,
        "feedback": None,
        "layer_dependencies": {}
    }
    
    print("\nStep 2: Generating code...")
    result = run_async_test(agent.process(input_data))
    
    print("\nStep 3: Validating results...")
    print("\n=== Code Generation Result ===")
    print(format_json(result))
    
    # Basic assertions
    assert result["status"] == "completed", f"Generation failed: {result.get('error', 'Unknown error')}"
    assert "generated_code" in result, "Generated code not found in result"
    assert "metadata" in result, "Metadata not found in result"
    
    print("\nStep 4: Saving output...")
    save_agent_output(output_dir, result, layer_spec["layer_id"])
    
    print("\n=== Test Completed Successfully ===")
    return result

if __name__ == "__main__":
    test_code_generation_agent() 