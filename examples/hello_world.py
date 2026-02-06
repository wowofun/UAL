import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ual import UAL

def main():
    print("=== UAL Hello World Example ===")
    
    # 1. 初始化 Agent
    agent = UAL(agent_id="Agent_001")
    
    # 2. 自然语言指令
    command = "Drone move to Target"
    print(f"Original Command: '{command}'")
    
    # 3. 编码 (Encode) -> Binary
    print("\n[Encoding...]")
    binary_data = agent.encode(command, receiver_id="Agent_002")
    print(f"UAL Binary (Hex): {binary_data.hex()[:64]}... ({len(binary_data)} bytes)")
    
    # 4. 传输 (模拟)
    # ... Network transmission ...
    
    # 5. 解码 (Decode) -> Understanding
    print("\n[Decoding...]")
    receiver = UAL(agent_id="Agent_002")
    result = receiver.decode(binary_data)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print("Decoded Result:")
    print(f"  Sender: {result['sender']}")
    print(f"  Timestamp: {result['timestamp']}")
    print(f"  Meaning: {result['natural_language']}")
    print(f"  Semantic Hash: {result['semantic_hash']}")

if __name__ == "__main__":
    main()
