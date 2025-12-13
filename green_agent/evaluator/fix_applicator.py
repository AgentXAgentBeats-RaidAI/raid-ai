"""Apply fixes submitted by purple agents"""
import subprocess
from pathlib import Path
from typing import Dict

class FixApplicator:
    def apply_patch(self, bug_dir: Path, patch: str) -> bool:
        patch_file = bug_dir / "fix.patch"
        with open(patch_file, 'w') as f:
            f.write(patch)
        
        result = subprocess.run(
            ["git", "apply", str(patch_file)],
            cwd=bug_dir,
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
    
    def apply_file_changes(self, bug_dir: Path, files: Dict[str, str]) -> bool:
        """Apply direct file changes"""
        try:
            for filepath, content in files.items():
                file_path = bug_dir / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
            return True
        except Exception as e:
            print(f"Error applying changes: {e}")
            return False
