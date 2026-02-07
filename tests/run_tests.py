import subprocess
import os
import sys
import time

def run_script(script_path):
    print(f"🔄 Running {script_path}...")
    start_time = time.time()
    try:
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=os.getcwd()  # Run from root
        )
        duration = time.time() - start_time
        return {
            "path": script_path,
            "success": result.returncode == 0,
            "duration": duration,
            "output": result.stdout,
            "error": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "path": script_path,
            "success": False,
            "duration": time.time() - start_time,
            "output": "",
            "error": str(e),
            "returncode": -1
        }

def main():
    scripts_to_test = [
        "examples/hello_world.py",
        "examples/virtual_agent_demo.py",
        "examples/the_great_demo.py",
        "tools/benchmark.py",
        # "tools/hub_sync.py" # Skip interactive or network-dependent tools if not mocked
    ]

    results = []
    print("🚀 Starting Global Test Suite for UAL...\n")

    for script in scripts_to_test:
        if not os.path.exists(script):
            print(f"⚠️  Skipping {script} (File not found)")
            continue
        
        res = run_script(script)
        results.append(res)
        
        status_icon = "✅" if res["success"] else "❌"
        print(f"{status_icon} {script} ({res['duration']:.2f}s)")
        if not res["success"]:
            print(f"   Error: {res['error'].strip()[:200]}...")

    print("\n================ TEST REPORT ================")
    print(f"Total Tests: {len(results)}")
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=============================================")
    
    # Detailed Failure Report
    if failed > 0:
        print("\n🔍 Failure Details:")
        for r in results:
            if not r['success']:
                print(f"\n--- {r['path']} ---")
                print(f"Exit Code: {r['returncode']}")
                print("Stderr:")
                print(r['error'])
                print("Stdout (Last 5 lines):")
                print("\n".join(r['output'].splitlines()[-5:]))

    # Generate Markdown Report
    with open("TEST_REPORT.md", "w") as f:
        f.write("# 🧪 UAL Global Test Report\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Summary:** {passed}/{len(results)} Passed\n\n")
        
        f.write("| Test Script | Status | Duration | Exit Code |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for r in results:
            icon = "✅ PASS" if r['success'] else "❌ FAIL"
            f.write(f"| `{r['path']}` | {icon} | {r['duration']:.2f}s | {r['returncode']} |\n")
        
        if failed > 0:
            f.write("\n## ❌ Failure Details\n")
            for r in results:
                if not r['success']:
                    f.write(f"\n### {r['path']}\n")
                    f.write("```bash\n")
                    f.write(r['error'])
                    f.write("\n```\n")

if __name__ == "__main__":
    main()
