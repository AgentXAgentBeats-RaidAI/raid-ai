"""JavaScript Bug Manager using BugsJS"""
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class JSManager:
    def __init__(self, bugsjs_path: str, workspace: str):
        self.bugsjs_path = Path(bugsjs_path)
        self.workspace = Path(workspace)
        self.projects_dir = self.bugsjs_path / "Projects"  # Capital P!
    
    def get_available_projects(self) -> List[str]:
        """Get list of all available BugsJS projects"""
        if not self.projects_dir.exists():
            return []
        return [d.name for d in self.projects_dir.iterdir() if d.is_dir()]
    
    def get_bug_info(self, project: str, bug_id: int) -> Dict:
        """Get information about a specific bug"""
        bugs_file = self.projects_dir / project / "bugs.json"
        
        if not bugs_file.exists():
            return {}
        
        with open(bugs_file, 'r') as f:
            bugs = json.load(f)
        
        for bug in bugs:
            if bug.get('bugId') == str(bug_id) or bug.get('bugId') == bug_id:
                return bug
        
        return {}
    
    def get_all_bugs(self, project: str) -> List[Dict]:
        """Get all bugs for a project"""
        bugs_file = self.projects_dir / project / "bugs.json"
        
        if not bugs_file.exists():
            return []
        
        with open(bugs_file, 'r') as f:
            return json.load(f)
    
    def checkout_bug(self, project: str, bug_id: int, buggy: bool = True) -> Path:
        """Checkout a bug to workspace"""
        bug_dir = self.workspace / f"{project}_{bug_id}_{'buggy' if buggy else 'fixed'}"
        
        if bug_dir.exists():
            shutil.rmtree(bug_dir)
        
        bug_info = self.get_bug_info(project, bug_id)
        if not bug_info:
            raise Exception(f"Bug {bug_id} not found in project {project}")
        
        tag = f"Bug-{bug_id}" if buggy else f"Bug-{bug_id}-fix"
        repo_url = bug_info.get('repositoryUrl', f"https://github.com/BugsJS/{project}")
        
        result = subprocess.run(
            ["git", "clone", repo_url, str(bug_dir)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to clone {project}: {result.stderr}")
        
        result = subprocess.run(
            ["git", "checkout", tag],
            cwd=bug_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to checkout tag {tag}: {result.stderr}")
        
        return bug_dir
    
    def compile_bug(self, bug_dir: Path) -> bool:
        """Install npm dependencies"""
        result = subprocess.run(
            ["npm", "install"],
            cwd=bug_dir,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def run_tests(self, bug_dir: Path) -> Dict:
        """Run tests using npm test"""
        result = subprocess.run(
            ["npm", "test"],
            cwd=bug_dir,
            capture_output=True,
            text=True,
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
        
        if not projects:
            return []
        
        bugs_per_project = max(1, count // len(projects))
        
        for project in projects:
            bugs = self.get_all_bugs(project)
            
            for i, bug in enumerate(bugs[:bugs_per_project]):
                if len(selected_bugs) >= count:
                    break
                
                bug_id = bug.get('bugId', i + 1)
                selected_bugs.append({
                    "language": "javascript",
                    "framework": "bugsjs",
                    "project": project,
                    "bug_id": bug_id,
                    "info": bug
                })
            
            if len(selected_bugs) >= count:
                break
        
        return selected_bugs[:count]
