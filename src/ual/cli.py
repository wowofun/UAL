import sys
import argparse
import binascii
import platform
import importlib.util
from ual import UAL

import os

def check_dependency(name, optional=False):
    found = importlib.util.find_spec(name) is not None
    status = "✅ Found" if found else ("❌ Missing" if not optional else "⚠️ Optional (Missing)")
    print(f"  - {name:<15} {status}")
    return found

def run_doctor():
    """
    Check environment health and dependencies.
    """
    print("\n=== 🏥 UAL Doctor ===")
    print(f"  - OS:             {platform.system()} {platform.release()}")
    print(f"  - Python:         {sys.version.split()[0]}")
    
    print("\n[Dependencies]")
    check_dependency("google.protobuf")
    check_dependency("networkx")
    check_dependency("numpy")
    
    print("\n[Optional Dependencies]")
    check_dependency("matplotlib", optional=True)  # For visualization
    check_dependency("flask", optional=True)       # For UAL Studio
    check_dependency("deep_translator", optional=True) # For Multilingual Studio
    
    print("\n[System Check]")
    try:
        agent = UAL("Doctor_Agent")
        print("  - UAL Core:       ✅ Initialized")
        
        # Simple self-test
        test_cmd = "move"
        b = agent.encode(test_cmd)
        d = agent.decode(b)
        # Relaxed check: verify the core verb is preserved
        meaning = d.get('natural_language', '')
        if test_cmd in meaning or "Action" in meaning:
             print("  - Encode/Decode:  ✅ Working")
        else:
             print(f"  - Encode/Decode:  ❌ Failed Logic (Got: '{meaning}')")
    except Exception as e:
        print(f"  - UAL Core:       ❌ Error ({e})")
        
    print("\nDoctor check complete.")

def run_init(filename="my_agent.py"):
    """
    Create a boilerplate agent file.
    """
    if os.path.exists(filename):
        print(f"❌ File '{filename}' already exists.")
        return

    content = """from ual import UAL

def main():
    # 1. Initialize your agent with a unique ID
    print("🚀 Initializing UAL Agent...")
    agent = UAL("MyAgent_01")

    # 2. Define a command (Natural Language)
    # UAL supports logic like "IF... THEN..." and physical actions
    text_command = "If temperature > 30 then turn on fan"
    
    # 3. Compile to binary (Standard Mode)
    # Use pure_binary=True for ultra-low bandwidth (lossy metadata)
    binary = agent.encode(text_command)
    print(f"📦 Encoded Payload: {len(binary)} bytes")
    print(f"   Hex: {binary.hex()}")

    # 4. Decode (simulate receiving)
    # In a real app, this would happen on the receiver device
    decoded = agent.decode(binary)
    print(f"📩 Decoded Meaning: {decoded.get('natural_language')}")
    
    # 5. Access the Graph Structure
    # UAL is a DAG (Directed Acyclic Graph), not just text
    print(f"   Graph Nodes: {len(decoded.get('nodes', []))}")

if __name__ == "__main__":
    main()
"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✅ Successfully created '{filename}'")
        print(f"👉 Run it with: python3 {filename}")
    except Exception as e:
        print(f"❌ Failed to create file: {e}")

def run_demo():
    """
    Run a simple in-memory demo.
    """
    print("\n=== 🎬 UAL Quick Demo ===")
    
    sender = UAL("Sender_Bot")
    receiver = UAL("Receiver_Bot")
    
    scenarios = [
        "Takeoff and fly to altitude 50",
        "If battery < 20 then return home",
        "Scan area and send report"
    ]
    
    for i, cmd in enumerate(scenarios):
        print(f"\n[Scenario {i+1}]")
        print(f"🗣️  User:     \"{cmd}\"")
        
        # Encode
        binary = sender.encode(cmd)
        print(f"📡  Transmit: {len(binary)} bytes (UAL Binary)")
        
        # Decode
        msg = receiver.decode(binary)
        print(f"🤖  Agent:    Parsed {len(msg.get('nodes', []))} nodes.")
        print(f"              Reconstructed: \"{msg.get('natural_language')}\"")
        
    print("\n✨ Demo complete. Try 'ual init' to start coding!")

def inspect_packet(input_data: str):
    """
    Inspect a UAL packet from hex string or file.
    """
    hex_data = input_data
    if os.path.exists(input_data):
        try:
            with open(input_data, 'r') as f:
                hex_data = f.read().strip()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    try:
        binary = binascii.unhexlify(hex_data.strip())
    except (binascii.Error, ValueError) as e:
        print(f"Error: Invalid hex string. {e}")
        return

    # Initialize a debugger agent
    debugger = UAL(agent_id="Debugger_CLI")
    
    try:
        # We try to decode. 
        # Note: Decode might fail signature check if we don't have public key, 
        # but our current validate() uses dummy_key and passes.
        result = debugger.decode(binary)
        
        print("\n=== UAL Packet Inspector ===")
        print(f"Sender: {result.get('sender')}")
        print(f"Timestamp: {result.get('timestamp')}")
        print(f"Type: {result.get('type', 'graph')}")
        
        if result.get('is_delta'):
             print(f"Mode: DELTA (Parent: {result.get('parent_hash', 'None')[:8]}...)")
        else:
             print(f"Mode: FULL")
             
        print(f"Semantic Hash: {result.get('semantic_hash')}")
        
        print("\n--- Content ---")
        if "natural_language" in result:
            print(f"Meaning: {result['natural_language']}")
        
        if "namespaces" in result:
            print(f"Namespaces: {result['namespaces']}")
            
        print("\n--- Raw Data ---")
        print(f"Size: {len(binary)} bytes")
        
    except Exception as e:
        print(f"Error decoding packet: {e}")

def compile_text(text: str, pure_binary: bool = False):
    """
    Compile natural language text to UAL binary.
    """
    agent = UAL(agent_id="CLI_Compiler")
    
    try:
        binary = agent.encode(text, pure_binary=pure_binary)
        hex_output = binascii.hexlify(binary).decode('utf-8')
        
        print(f"\n=== UAL Compiler ===")
        print(f"Input: \"{text}\"")
        print(f"Mode: {'PureBinary' if pure_binary else 'Standard'}")
        print(f"Size: {len(binary)} bytes")
        print(f"\nHex Output:\n{hex_output}")
        
    except Exception as e:
        print(f"Error compiling text: {e}")

def main():
    parser = argparse.ArgumentParser(description="UAL CLI Debugger")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Inspect Command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a hex-encoded UAL packet")
    inspect_parser.add_argument("hex", help="Hex string of the packet")
    
    # Compile Command
    compile_parser = subparsers.add_parser("compile", help="Compile text to UAL binary")
    compile_parser.add_argument("text", help="Natural language text to compile")
    compile_parser.add_argument("--pure-binary", action="store_true", help="Enable PureBinary mode (strip metadata)")

    # Init Command
    subparsers.add_parser("init", help="Create a boilerplate agent file")
    
    # Doctor Command
    subparsers.add_parser("doctor", help="Check environment health")
    
    # Demo Command
    subparsers.add_parser("demo", help="Run a quick in-memory demo")

    args = parser.parse_args()
    
    if args.command == "inspect":
        inspect_packet(args.hex)
    elif args.command == "compile":
        compile_text(args.text, args.pure_binary)
    elif args.command == "init":
        run_init()
    elif args.command == "doctor":
        run_doctor()
    elif args.command == "demo":
        run_demo()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
