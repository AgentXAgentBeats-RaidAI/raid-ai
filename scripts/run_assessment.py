#!/usr/bin/env python3
"""
Assessment execution script for RAID-AI Green Agent
Demonstrates reproducibility by running identical assessments multiple times
"""

import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, List

class AssessmentRunner:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_health(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Green agent not running: {e}")
            return False
    
    def get_benchmark_info(self) -> Dict:
        response = self.session.get(f"{self.base_url}/benchmark/info")
        return response.json()
    
    def start_assessment(self, agent_id: str, bug_indices: List[int] = None) -> str:
        payload = {
            "agent_id": agent_id,
            "docker_image": "mock-purple-agent:latest",  # Placeholder
            "config": {"timeout": 60},
            "bug_indices": bug_indices
        }
        
        response = self.session.post(f"{self.base_url}/assess", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"🚀 Started assessment {result['assessment_id']} for agent '{agent_id}'")
            return result['assessment_id']
        else:
            raise Exception(f"Failed to start assessment: {response.text}")
    
    def wait_for_assessment(self, assessment_id: str) -> Dict:
        print(f"⏳ Waiting for assessment {assessment_id} to complete...")
        
        while True:
            response = self.session.get(f"{self.base_url}/assess/{assessment_id}")
            status_info = response.json()
            
            status = status_info["status"]
            if status == "completed":
                print(f"✅ Assessment {assessment_id} completed!")
                return status_info
            elif status == "failed":
                print(f"❌ Assessment {assessment_id} failed: {status_info.get('error', 'Unknown error')}")
                return status_info
            else:
                progress = status_info.get("progress", {})
                completed = progress.get("completed", 0)
                total = progress.get("total", 0)
                print(f"   Progress: {completed}/{total} bugs processed...")
                time.sleep(5)  # Wait 5 seconds before checking again
    
    def get_leaderboard(self) -> Dict:
        response = self.session.get(f"{self.base_url}/leaderboard")
        return response.json()
    
    def run_reproducibility_test(self, agent_id: str, num_runs: int = 2, bug_subset: List[int] = None) -> List[Dict]:
        print(f"\n Running reproducibility test for '{agent_id}' ({num_runs} runs)")
        
        if bug_subset is None:
            # Use first 5 bugs for faster testing
            bug_subset = list(range(5))
        
        results = []
        
        for run_num in range(1, num_runs + 1):
            print(f"\n--- Run {run_num}/{num_runs} ---")
            
            # Start assessment
            assessment_id = self.start_assessment(f"{agent_id}_run_{run_num}", bug_subset)
            
            # Wait for completion
            result = self.wait_for_assessment(assessment_id)
            
            if result["status"] == "completed":
                # Extract key metrics for comparison
                assessment_results = result.get("results", [])
                metrics = {
                    "assessment_id": assessment_id,
                    "agent_id": f"{agent_id}_run_{run_num}",
                    "run_number": run_num,
                    "total_bugs": len(assessment_results),
                    "avg_total_score": sum(r["total_score"] for r in assessment_results) / len(assessment_results) if assessment_results else 0,
                    "avg_correctness": sum(r["correctness_score"] for r in assessment_results) / len(assessment_results) if assessment_results else 0,
                    "bugs_fixed": sum(1 for r in assessment_results if r["correctness_score"] > 0.8),
                    "timestamp": result.get("completed_at", "")
                }
                results.append(metrics)
                
                print(f"   Avg Score: {metrics['avg_total_score']:.3f}")
                print(f"   Bugs Fixed: {metrics['bugs_fixed']}/{metrics['total_bugs']}")
            
            # Small delay between runs
            time.sleep(2)
        
        return results
    
    def analyze_reproducibility(self, results: List[Dict]) -> None:
        if len(results) < 2:
            print("❌ Need at least 2 runs to analyze reproducibility")
            return
        
        print(f"\n📊 Reproducibility Analysis ({len(results)} runs)")
        print("=" * 50)
        
        # Extract scores for comparison
        total_scores = [r["avg_total_score"] for r in results]
        bugs_fixed = [r["bugs_fixed"] for r in results]
        
        # Calculate variance
        score_variance = sum((score - sum(total_scores)/len(total_scores))**2 for score in total_scores) / len(total_scores)
        bugs_variance = sum((bugs - sum(bugs_fixed)/len(bugs_fixed))**2 for bugs in bugs_fixed) / len(bugs_fixed)
        
        print(f"Average Total Score: {sum(total_scores)/len(total_scores):.3f} (variance: {score_variance:.6f})")
        print(f"Average Bugs Fixed: {sum(bugs_fixed)/len(bugs_fixed):.1f} (variance: {bugs_variance:.3f})")
        
        # Check if results are identical (good for reproducibility)
        score_identical = all(abs(score - total_scores[0]) < 0.001 for score in total_scores)
        bugs_identical = all(bugs == bugs_fixed[0] for bugs in bugs_fixed)
        
        print(f"\nReproducibility Status:")
        print(f"  Scores identical: {'✅ Yes' if score_identical else '⚠️ No'}")
        print(f"  Bugs fixed identical: {'✅ Yes' if bugs_identical else '⚠️ No'}")
        
        if score_identical and bugs_identical:
            print("🎉 Perfect reproducibility achieved!")
        elif score_variance < 0.01 and bugs_variance < 1:
            print("✅ Good reproducibility (small variance)")
        else:
            print("⚠️ Results show variance - check for non-deterministic behavior")

def main():
    runner = AssessmentRunner()
    
    # Check if green agent is running
    if not runner.check_health():
        print("Please start the green agent first:")
        print("  python -m green_agent.api.a2a_interface")
        sys.exit(1)
    
    # Get benchmark info
    print("📋 Benchmark Information:")
    info = runner.get_benchmark_info()
    print(f"  Name: {info['name']}")
    print(f"  Total Bugs: {info['total_bugs']}")
    print(f"  Languages: {', '.join(info['languages'])}")
    
    # Run reproducibility test
    test_agent = "test-purple-agent"
    results = runner.run_reproducibility_test(test_agent, num_runs=2)
    
    # Analyze results
    runner.analyze_reproducibility(results)
    
    # Save results for leaderboard
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"data/reproducibility_test_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {results_file}")
    
    # Show current leaderboard
    print(f"\n🏆 Current Leaderboard:")
    leaderboard = runner.get_leaderboard()
    for i, entry in enumerate(leaderboard["leaderboard"][:5], 1):
        print(f"  {i}. {entry['agent_id']} - Score: {entry['avg_score']:.3f} ({entry['bugs_fixed']} bugs fixed)")

if __name__ == "__main__":
    main()