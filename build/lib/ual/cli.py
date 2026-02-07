import sys
import argparse
import binascii
from ual import UAL

import os

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

def main():
    parser = argparse.ArgumentParser(description="UAL CLI Debugger")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Inspect Command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a hex-encoded UAL packet")
    inspect_parser.add_argument("hex", help="Hex string of the packet")
    
    args = parser.parse_args()
    
    if args.command == "inspect":
        inspect_packet(args.hex)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
