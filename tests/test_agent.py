#!/usr/bin/env python3
"""
Test script to verify the agent works correctly.
"""

from agent_runner import run_agent

def test_agent():
    """Test the agent functionality."""
    print("Testing agent functionality...")
    
    test_prompt = "Hello, can you help me understand what this agent does?"
    job_name = "test-job"
    
    try:
        result = run_agent(test_prompt, job_name)
        print(f"Agent response: {result}")
        return True
    except Exception as e:
        print(f"Error testing agent: {e}")
        return False

if __name__ == "__main__":
    test_agent() 