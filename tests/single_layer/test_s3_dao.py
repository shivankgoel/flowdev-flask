import json
from . import run_async_test, create_test_agent, get_user_document_spec

def test_user_document_dao():
    """Test generating code for user document S3 DAO layer"""
    agent = create_test_agent()
    layer_spec = get_user_document_spec()
    
    result = run_async_test(agent.process({"layer_spec": layer_spec}))
    
    print("\n=== User Document S3 DAO Generation Result ===")
    print(json.dumps(result, indent=2))
    
    # Basic assertions
    assert result["status"] == "completed"
    assert layer_spec["layer_id"] in result["generated_code"]
    assert "UserDocumentS3DAO" in result["generated_code"][layer_spec["layer_id"]]
    
    return result

if __name__ == "__main__":
    test_user_document_dao() 