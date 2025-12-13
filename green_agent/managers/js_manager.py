"""JavaScript Bug Manager using BugsJS"""
import subprocess
import csv
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class JSManager:
    def __init__(self, bugsjs_path: str, workspace: str):
        self.bugsjs_path = Path(bugsjs_path)
        self.workspace = Path(workspace)
        self.projects_dir = self.bugsjs_path / "Projects"
    
    def get_available_projects(self) -> List[str]:
        if not self.projects_dir.exists():
            return []
        return [d.name for d in self.projects_dir.iterdir() if d.is_dir()]
    
    def get_bug_info(self, project: str, bug_id: int) -> Dict:
        bugs_csv = self.projects_dir / project / f"{project}_bugs.csv"
        
        if not bugs_csv.exists():
            return {}
        
        with open(bugs_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if int(row.get('ID', 0)) == bug_id:
                    return row
        
        return {}
    
    def get_all_bugs(self, project: str) -> List[Dict]:
        bugs_csv = self.projects_dir / project / f"{project}_bugs.csv"
        
        if not bugs_csv.exists():
            return []
        
        bugs = []
        with open(bugs_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                bugs.append(row)
        
        return bugs
    
    def checkout_bug(self, project: str, bug_id: int, buggy: bool = True) -> Path:
        """Extract bug ZIP file to workspace
        
        BugsJS stores bugs as ZIP files: Eslint-1.zip, Eslint-2.zip, etc.
        """
        bug_dir = self.workspace / f"{project}_{bug_id}_{'buggy' if buggy else 'fixed'}"
        
        # Clean up if exists
        if bug_dir.exists():
            shutil.rmtree(bug_dir)
        
        # Find the ZIP file
        zip_file = self.projects_dir / project / f"{project}-{bug_id}.zip"
        
        if not zip_file.exists():
            raise Exception(f"Bug ZIP not found: {zip_file}")
        
        # Extract the ZIP
        shutil.unpack_archive(zip_file, bug_dir)
        
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
            
            # Select first N bugs from this project
            for bug in bugs[:bugs_per_project]:
                if len(selected_bugs) >= count:
                    break
                
                try:
                    bug_id = int(bug.get('ID', 0))
                    if bug_id > 0:
                        selected_bugs.append({
                            "language": "javascript",
                            "framework": "bugsjs",
                            "project": project,
                            "bug_id": bug_id,
                            "info": {
                                "commit": bug.get('Commit', ''),
                                "issue_id": bug.get('Issue ID', ''),
                                "type": bug.get('Type', '')
                            }
                        })
                except (ValueError, KeyError) as e:
                    print(f"WARNING: Error processing bug in {project}: {e}")
                    continue
            
            if len(selected_bugs) >= count:
                break
        
        return selected_bugs[:count]
