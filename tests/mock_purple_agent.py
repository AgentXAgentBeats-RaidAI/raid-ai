"""Mock purple agent for testing the green agent"""
import requests
import os
import time

class MockPurpleAgent:
    def __init__(self, api_url=None):
        if api_url is None:
            api_url = os.getenv("GREEN_AGENT_URL", "http://localhost:8000")
        self.api_url = api_url
    
    def get_benchmark_info(self):
        r = requests.get(f"{self.api_url}/benchmark/info")
        return r.json()
    
    def get_bug(self, bug_index):
        r = requests.get(f"{self.api_url}/bugs/{bug_index}")
        return r.json()
    
    def submit_fix(self, bug_index, patch):
        r = requests.post(f"{self.api_url}/evaluate", json={
            "bug_index": bug_index,
            "patch": patch
        })
        return r.json()

# Test
if __name__ == "__main__":
    print("Starting Purple Agent...")
    agent = MockPurpleAgent()
    
    # Wait for green agent to be ready
    print(f"Connecting to Green Agent at {agent.api_url}")
    for attempt in range(10):
        try:
            info = agent.get_benchmark_info()
            print(f"✓ Connected! Benchmark has {info['total_bugs']} bugs")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1}/10: Waiting for Green Agent... ({e})")
            time.sleep(5)
    else:
        print("❌ Failed to connect to Green Agent")
        exit(1)
    
    # Get first bug
    try:
        bug = agent.get_bug(0)
        print(f"First bug: {bug['project']} #{bug['bug_id']}")
        
        # Submit a dummy fix
        result = agent.submit_fix(0, "# Dummy fix")
        print(f"Fix submission result: {result}")
        
        print("✓ Purple Agent test completed successfully")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    # Keep running for testing
    print("Purple Agent is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        print("Purple Agent stopped.")
