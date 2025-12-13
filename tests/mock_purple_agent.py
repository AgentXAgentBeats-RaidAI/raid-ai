"""Mock purple agent for testing the green agent"""
import requests

class MockPurpleAgent:
    def __init__(self, api_url="http://localhost:8000"):
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
    agent = MockPurpleAgent()
    info = agent.get_benchmark_info()
    print(f"Benchmark has {info['total_bugs']} bugs")
    
    # Get first bug
    bug = agent.get_bug(0)
    print(f"First bug: {bug['project']} #{bug['bug_id']}")
