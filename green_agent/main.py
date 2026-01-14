"""Main Green Agent - RAID-AI Benchmark"""
import yaml
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from green_agent.managers.java_manager import JavaManager
from green_agent.managers.python_manager import PythonManager
from green_agent.managers.js_manager import JSManager
from green_agent.evaluator.scorer import Scorer, FixScore

class RAIDGreenAgent:    
    def __init__(self, config_path: str = None):
        # Use Docker config if no path specified and in Docker environment
        if config_path is None:
            if Path("/app/configs/docker_config.yaml").exists():
                config_path = "/app/configs/docker_config.yaml"
            else:
                config_path = "configs/agent_config.yaml"
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize managers
        paths = self.config['paths']
        workspace = paths['workspace']
        
        self.java_manager = JavaManager(paths['defects4j'], workspace)
        self.python_manager = PythonManager(paths['bugsinpy'], workspace)
        self.js_manager = JSManager(paths['bugsjs'], workspace)
        
        # Initialize scorer
        self.scorer = Scorer(self.config['evaluation'])
        
        # Selected bugs catalog
        self.bugs_catalog = []
    
    def initialize_benchmark(self):
        print("Initializing RAID-AI Benchmark...")
        
        # Select bugs from each framework
        java_count = self.config['bugs']['java']['count']
        python_count = self.config['bugs']['python']['count']
        js_count = self.config['bugs']['javascript']['count']
        
        print(f"  Selecting {java_count} Java bugs...")
        java_bugs = self.java_manager.select_bugs(java_count)
        self.bugs_catalog.extend(java_bugs)
        
        print(f"  Selecting {python_count} Python bugs...")
        python_bugs = self.python_manager.select_bugs(python_count)
        self.bugs_catalog.extend(python_bugs)
        
        print(f"  Selecting {js_count} JavaScript bugs...")
        js_bugs = self.js_manager.select_bugs(js_count)
        self.bugs_catalog.extend(js_bugs)
        
        print(f"Benchmark initialized with {len(self.bugs_catalog)} bugs")
        print(f"   - Java: {len(java_bugs)}")
        print(f"   - Python: {len(python_bugs)}")
        print(f"   - JavaScript: {len(js_bugs)}")
        
        # Save catalog
        self._save_catalog()
    
    def _save_catalog(self):
        catalog_path = 'bugs/catalog.json'
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(catalog_path), exist_ok=True)
        
        with open(catalog_path, 'w') as f:
            json.dump(self.bugs_catalog, f, indent=2)
        print(f"Catalog saved to {catalog_path}")
    
    def get_bug(self, index: int) -> Optional[Dict]:
        if 0 <= index < len(self.bugs_catalog):
            return self.bugs_catalog[index]
        return None
    
    def evaluate_fix(self, bug_index: int, fixed_code_path: str) -> FixScore:
        """Evaluate a fix submitted by a purple agent
        
        Args:
            bug_index: Index of the bug in catalog
            fixed_code_path: Path to the fixed code
        
        Returns:
            FixScore object with evaluation results
        """
        bug = self.get_bug(bug_index)
        if not bug:
            raise ValueError(f"Invalid bug index: {bug_index}")
        
        print(f"🧪 Evaluating fix for {bug['language']} bug: {bug['project']} #{bug['bug_id']}")
        
        start_time = time.time()
        
        # Get appropriate manager
        if bug['language'] == 'java':
            manager = self.java_manager
        elif bug['language'] == 'python':
            manager = self.python_manager
        else:
            manager = self.js_manager
        
        # Checkout the bug
        bug_dir = manager.checkout_bug(bug['project'], bug['bug_id'], buggy=True)
        
        # Apply the fix (this would be implemented based on how purple agent submits)
        # For now, placeholder
        
        # Compile
        compile_success = manager.compile_bug(bug_dir)
        if not compile_success:
            elapsed = time.time() - start_time
            return self.scorer.score_fix(bug, {'success': False}, elapsed, 0)
        
        # Run tests
        test_result = manager.run_tests(bug_dir)
        elapsed = time.time() - start_time
        
        # Calculate patch size (placeholder - would need diff logic)
        patch_size = 10  # TODO: Calculate actual diff
        
        # Score the fix
        score = self.scorer.score_fix(bug, test_result, elapsed, patch_size)
        
        print(f"   Score: {score.total_score:.2f} (Correctness: {score.correctness:.2f})")
        
        return score
    
    def get_leaderboard(self, scores: List[FixScore]) -> Dict:
        return self.scorer.aggregate_scores(scores)
    
    def export_benchmark_info(self) -> Dict:
        return {
            'name': self.config['agent']['name'],
            'version': self.config['agent']['version'],
            'total_bugs': len(self.bugs_catalog),
            'languages': ['java', 'python', 'javascript'],
            'evaluation_criteria': self.config['evaluation']['scoring'],
            'timeout': self.config['evaluation']['timeout_per_bug'],
            'bugs_by_language': {
                'java': len([b for b in self.bugs_catalog if b['language'] == 'java']),
                'python': len([b for b in self.bugs_catalog if b['language'] == 'python']),
                'javascript': len([b for b in self.bugs_catalog if b['language'] == 'javascript'])
            }
        }

if __name__ == "__main__":
    agent = RAIDGreenAgent()
    agent.initialize_benchmark()
    
    # Export info
    info = agent.export_benchmark_info()
    print(f"\n Benchmark Info:")
    print(json.dumps(info, indent=2))
