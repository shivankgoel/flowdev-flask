import asyncio
from typing import Dict, Any, List
from app.agents.chatgpt_agent import ChatGPTAgent
from tests.single_layer import get_flight_booking_spec, get_user_document_spec
from tests.two_layers import get_flight_booking_layers
from tests.three_layers import get_flight_booking_three_layers

def run_async_test(coro):
    """Helper function to run async tests"""
    return asyncio.run(coro)

def create_test_agent() -> ChatGPTAgent:
    """Helper function to create a test agent"""
    return ChatGPTAgent()

async def test_single_layer(agent: ChatGPTAgent, spec: Dict[str, Any]):
    """Test single layer generation"""
    result = await agent.generate_code(spec)
    print(f"\nGenerated code for single layer:\n{result}")
    return result

async def test_two_layers(agent: ChatGPTAgent, specs: List[Dict[str, Any]]):
    """Test two layer generation"""
    result = await agent.generate_code(specs)
    print(f"\nGenerated code for two layers:\n{result}")
    return result

async def test_three_layers(agent: ChatGPTAgent, specs: List[Dict[str, Any]]):
    """Test three layer generation"""
    result = await agent.generate_code(specs)
    print(f"\nGenerated code for three layers:\n{result}")
    return result

async def run_all_tests():
    """Run all test cases"""
    agent = create_test_agent()
    
    # Test single layer generation
    print("\nTesting single layer generation...")
    await test_single_layer(agent, get_flight_booking_spec())
    await test_single_layer(agent, get_user_document_spec())
    
    # Test two layer generation
    print("\nTesting two layer generation...")
    await test_two_layers(agent, get_flight_booking_layers())
    
    # Test three layer generation
    print("\nTesting three layer generation...")
    await test_three_layers(agent, get_flight_booking_three_layers())

if __name__ == "__main__":
    run_async_test(run_all_tests()) 