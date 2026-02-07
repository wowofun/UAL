import time
import json
import random
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ual.core import UAL
from ual.parser import RuleBasedParser

def run_benchmark():
    print("🚀 Running UAL vs JSON Benchmark...")
    print("-" * 60)
    
    agent = UAL("Bench_Agent")
    
    # Test Data
    commands = [
        "Move to kitchen",
        "Scan area",
        "Drone return to base",
        "Stop and wait",
        "Detect obstacle at 10 meters"
    ]
    
    iterations = 1000
    
    # 1. JSON-RPC Benchmark
    json_start = time.time()
    total_json_size = 0
    
    for _ in range(iterations):
        cmd = random.choice(commands)
        # Mock JSON-RPC format
        payload = {
            "jsonrpc": "2.0",
            "method": "execute_command",
            "params": {"command": cmd, "urgency": "high"},
            "id": 1
        }
        json_bytes = json.dumps(payload).encode('utf-8')
        total_json_size += len(json_bytes)
        
    json_time = (time.time() - json_start) * 1000 # ms
    
    # 2. UAL Benchmark
    ual_start = time.time()
    total_ual_size = 0
    
    for _ in range(iterations):
        cmd = random.choice(commands)
        ual_bytes = agent.encode(cmd)
        total_ual_size += len(ual_bytes)
        
    ual_time = (time.time() - ual_start) * 1000 # ms
    
    # Results
    avg_json_size = total_json_size / iterations
    avg_ual_size = total_ual_size / iterations
    
    print(f"Iterations: {iterations}")
    print(f"{'Metric':<20} | {'JSON-RPC':<15} | {'UAL v0.2':<15} | {'Improvement':<15}")
    print("-" * 75)
    print(f"{'Avg Payload Size':<20} | {avg_json_size:.1f} bytes      | {avg_ual_size:.1f} bytes      | {avg_json_size/avg_ual_size:.1f}x Smaller")
    print(f"{'Total Time':<20} | {json_time:.1f} ms         | {ual_time:.1f} ms         | {json_time/ual_time:.1f}x Faster")
    print(f"{'Avg Latency':<20} | {json_time/iterations:.3f} ms       | {ual_time/iterations:.3f} ms       | -")
    print("-" * 75)

if __name__ == "__main__":
    run_benchmark()
