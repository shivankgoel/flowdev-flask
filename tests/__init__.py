import asyncio
from typing import Dict, Any, List
from app.agents.chatgpt_agent import ChatGPTAgent

def run_async_test(coro):
    """Helper function to run async tests"""
    return asyncio.run(coro)

def create_test_agent() -> ChatGPTAgent:
    """Helper function to create a test agent"""
    return ChatGPTAgent() 