"""Python Bug Manager using BugsInPy"""
import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class PythonManager:
    def __init__(self, bugsinpy_path: str, workspace: str):
        self.bugsinpy_path = Path(bugsinpy_path)
        self.workspace = Path(workspace)
        self.bugsinpy_bin = self.bugsinpy_path / "framework" / "bin"
        
        self.env = os.environ.copy()
        self.env['PATH'] = f"{self.bugsinpy_bin}:{self.env['PATH']}"
    
    def get_available_projects(self) -> List[str]:
        """Get list of all available BugsInPy projects"""
        projects_dir = self.bugsinpy_path / "projects"
        return [d.name for d in projects_dir.iterdir() if d.is_dir()]
    
    def get_bug_info(self, project: str, bug_id: int) -> Dict:
        """Get information about a specific bug"""
        result = subprocess.run(
            ["bugsinpy-info", "-p", project, "-i", str(bug_id)],
            capture_output=True,
            text=True,
            env=self.env
        )
        
        info = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        return info
    
    def checkout_bug(self, project: str, bug_id: int, buggy: bool = True) -> Path:
        """Checkout a bug to workspace"""
        version = "0" if buggy else "1"
        bug_dir = self.workspace / f"{project}_{bug_id}_{'buggy' if buggy else 'fixed'}"
        
        if bug_dir.exists():
            shutil.rmtree(bug_dir)
        
        result = subprocess.run(
            ["bugsinpy-checkout", "-p", project, "-v", version, "-i", str(bug_id), "-w", str(bug_dir)],
            capture_output=True,
            text=True,
            env=self.env
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to checkout {project} bug {bug_id}: {result.stderr}")
        
        return bug_dir
    
    def compile_bug(self, bug_dir: Path) -> bool:
        """Compile/setup the checked out bug"""
        result = subprocess.run(
            ["bugsinpy-compile"],
            cwd=bug_dir,
            capture_output=True,
            text=True,
            env=self.env
        )
        return result.returncode == 0
    
    def run_tests(self, bug_dir: Path) -> Dict:
        """Run tests on the bug"""
        result = subprocess.run(
            ["bugsinpy-test"],
            cwd=bug_dir,
            capture_output=True,
            text=True,
            env=self.env,
            timeout=300
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "stderr": result.stderr
        }
    
    def select_bugs(self, count: int = 30) -> List[Dict]:
        """Select a diverse set of bugs for the benchmark"""
        projects = self.get_available_projects()
        selected_bugs = []
        
        bugs_per_project = max(1, count // len(projects))
        
        for project in projects:
            # Bugs are in bugs/ subdirectory, numbered 1, 2, 3, etc.
            bugs_dir = self.bugsinpy_path / "projects" / project / "bugs"
            if not bugs_dir.exists():
                continue
            
            # Get list of bug directories (numbered folders)
            bug_ids = []
            for item in bugs_dir.iterdir():
                if item.is_dir() and item.name.isdigit():
                    bug_ids.append(int(item.name))
            
            bug_ids.sort()
            
            # Select first N bugs
            for bug_id in bug_ids[:bugs_per_project]:
                if len(selected_bugs) >= count:
                    break
                selected_bugs.append({
                    "language": "python",
                    "framework": "bugsinpy",
                    "project": project,
                    "bug_id": bug_id
                })
            
            if len(selected_bugs) >= count:
                break
        
        return selected_bugs[:count]
