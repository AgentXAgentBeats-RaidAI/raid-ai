"""Test script for bug managers"""
from green_agent.managers.java_manager import JavaManager
from green_agent.managers.python_manager import PythonManager
from green_agent.managers.js_manager import JSManager

# Test Java Manager
print("=== Testing Java Manager ===")
java_mgr = JavaManager(
    "/home/jo/Documents/school/raid-ai/defects4j",
    "/tmp/raid-test"
)
print(f"Available Java projects: {java_mgr.get_available_projects()[:5]}")
java_bugs = java_mgr.select_bugs(count=5)
print(f"Selected {len(java_bugs)} Java bugs")
for bug in java_bugs:
    print(f"  - {bug['project']} #{bug['bug_id']}")

# Test Python Manager
print("\n=== Testing Python Manager ===")
python_mgr = PythonManager(
    "/home/jo/Documents/school/raid-ai/BugsInPy",
    "/tmp/raid-test"
)
print(f"Available Python projects: {python_mgr.get_available_projects()[:5]}")
python_bugs = python_mgr.select_bugs(count=5)
print(f"Selected {len(python_bugs)} Python bugs")
for bug in python_bugs:
    print(f"  - {bug['project']} #{bug['bug_id']}")

# Test JS Manager
print("\n=== Testing JS Manager ===")
js_mgr = JSManager(
    "/home/jo/Documents/school/raid-ai/bugsjs-dataset",
    "/tmp/raid-test"
)
print(f"Available JS projects: {js_mgr.get_available_projects()[:5]}")
js_bugs = js_mgr.select_bugs(count=5)
print(f"Selected {len(js_bugs)} JS bugs")
for bug in js_bugs:
    print(f"  - {bug['project']} #{bug['bug_id']}")

print("\n✅ All managers working!")
