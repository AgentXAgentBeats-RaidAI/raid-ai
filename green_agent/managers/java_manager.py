"""Java Bug Manager using Defects4J"""
import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class JavaManager:
    def __init__(self, defects4j_path: str, workspace: str):
        self.defects4j_path = Path(defects4j_path)
        self.workspace = Path(workspace)
        self.defects4j_bin = self.defects4j_path / "framework" / "bin" / "defects4j"
        
    def get_available_projects(self) -> List[str]:
        """Get list of all available Defects4J projects"""
        result = subprocess.run(
            [str(self.defects4j_bin), "pids"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n')
    
    def get_bug_info(self, project: str, bug_id: int) -> Dict:
        """Get information about a specific bug"""
        result = subprocess.run(
            [str(self.defects4j_bin), "info", "-p", project, "-b", str(bug_id)],
            capture_output=True,
            text=True
        )
        # Parse the output into a dict
        info = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        return info
    
    def checkout_bug(self, project: str, bug_id: int, buggy: bool = True) -> Path:
        """Checkout a bug to workspace"""
        version = f"{bug_id}b" if buggy else f"{bug_id}f"
        bug_dir = self.workspace / f"{project}_{bug_id}_{'buggy' if buggy else 'fixed'}"
        
        # Clean up if exists
        if bug_dir.exists():
            shutil.rmtree(bug_dir)
        
        # Checkout
        result = subprocess.run(
            [str(self.defects4j_bin), "checkout", "-p", project, "-v", version, "-w", str(bug_dir)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to checkout {project} bug {bug_id}: {result.stderr}")
        
        return bug_dir
    
    def compile_bug(self, bug_dir: Path) -> bool:
        """Compile the checked out bug"""
        result = subprocess.run(
            [str(self.defects4j_bin), "compile"],
            cwd=bug_dir,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def run_tests(self, bug_dir: Path, test_suite: str = "trigger") -> Dict:
        """Run tests on the bug
        
        Args:
            bug_dir: Directory containing the checked out bug
            test_suite: "trigger" for triggering tests, "relevant" for relevant tests, "all" for all tests
        """
        cmd = [str(self.defects4j_bin), "test"]
        if test_suite == "trigger":
            cmd.append("-t")  # Only run triggering tests
        elif test_suite == "relevant":
            cmd.append("-r")  # Only run relevant tests
        
        result = subprocess.run(
            cmd,
            cwd=bug_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Parse results
        output = result.stdout
        return {
            "success": result.returncode == 0,
            "output": output,
            "failing_tests": self._parse_failing_tests(output)
        }
    
    def _parse_failing_tests(self, output: str) -> List[str]:
        """Parse failing tests from defects4j test output"""
        failing = []
        for line in output.split('\n'):
            if line.startswith('Failing tests:'):
                # Parse the list of failing tests
                continue
            elif line.strip().startswith('-'):
                test_name = line.strip()[2:].strip()
                if test_name:
                    failing.append(test_name)
        return failing
    
    def get_coverage(self, bug_dir: Path) -> Dict:
        """Get code coverage information"""
        result = subprocess.run(
            [str(self.defects4j_bin), "coverage"],
            cwd=bug_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Parse coverage data
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    
    def select_bugs(self, count: int = 30) -> List[Dict]:
        """Select a diverse set of bugs for the benchmark"""
        projects = self.get_available_projects()
        selected_bugs = []
        
        # Distribute bugs across projects
        bugs_per_project = max(1, count // len(projects))
        
        for project in projects:
            # Get bug count for this project
            result = subprocess.run(
                [str(self.defects4j_bin), "bids", "-p", project],
                capture_output=True,
                text=True
            )
            bug_ids = result.stdout.strip().split('\n')
            
            # Select first N bugs from this project
            for bug_id in bug_ids[:bugs_per_project]:
                if len(selected_bugs) >= count:
                    break
                selected_bugs.append({
                    "language": "java",
                    "framework": "defects4j",
                    "project": project,
                    "bug_id": int(bug_id)
                })
            
            if len(selected_bugs) >= count:
                break
        
        return selected_bugs[:count]
