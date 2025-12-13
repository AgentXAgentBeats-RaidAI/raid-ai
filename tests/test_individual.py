from green_agent.managers.java_manager import JavaManager
from green_agent.managers.python_manager import PythonManager

# Test Java Manager - Checkout and compile a bug
print("=== Testing Java Bug Checkout ===")
java_mgr = JavaManager(
    "/home/jo/Documents/school/raid-ai/defects4j",
    "/tmp/raid-test"
)

# Get info about a specific bug
info = java_mgr.get_bug_info("Chart", 1)
print(f"Bug info: {info}")

# Checkout the buggy version
print("\nChecking out Chart bug 1...")
bug_dir = java_mgr.checkout_bug("Chart", 1, buggy=True)
print(f"Checked out to: {bug_dir}")

# Compile
print("\nCompiling...")
compile_success = java_mgr.compile_bug(bug_dir)
print(f"Compile success: {compile_success}")

# Run tests
print("\nRunning tests...")
test_results = java_mgr.run_tests(bug_dir)
print(f"Tests passed: {test_results['success']}")
print(f"Failing tests: {test_results['failing_tests']}")

print("\n=== Testing Python Bug Checkout ===")
python_mgr = PythonManager(
    "/home/jo/Documents/school/raid-ai/BugsInPy",
    "/tmp/raid-test"
)

# Checkout a Python bug
print("\nChecking out youtube-dl bug 1...")
bug_dir = python_mgr.checkout_bug("youtube-dl", 1, buggy=True)
print(f"Checked out to: {bug_dir}")

# Compile
print("\nCompiling...")
compile_success = python_mgr.compile_bug(bug_dir)
print(f"Compile success: {compile_success}")

print("\n✅ Individual manager tests complete!")
