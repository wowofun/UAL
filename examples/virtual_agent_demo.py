import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from ual.llm_bridge import UALBridge
from ual import ual_pb2

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

def demo_software_agents():
    print_separator("UAL Virtual Agent Demo")
    print("Scenario: A 'User Agent' (Software) talks to a 'Service Agent' (Software)")
    print("Goal: Verify UAL works for non-hardware scenarios (Pure Logic/Data flow)\n")

    # 1. Initialize Agents
    user_agent = UALBridge("User_Bot_01")
    service_agent = UALBridge("Weather_Service_Bot")

    # 2. User Agent "Speaks" (Encodes Request)
    # In a real app, this text comes from an LLM (e.g. GPT-4)
    request_text = "If temperature is high then turn on fan"
    print(f"🤖 User Bot: '{request_text}'")
    
    # Simulate sending over network (User -> Service)
    # The 'speak' method returns a dict with the hex payload
    packet = user_agent.speak(request_text)
    
    if packet.get("status") == "error":
        print(f"❌ Error encoding UAL: {packet.get('message')}")
        return

    hex_data = packet['ual_binary_hex']
    
    print(f"📡 Network: Transmitting {len(bytes.fromhex(hex_data))} bytes of UAL Binary...")
    print(f"   Hex: {hex_data}")
    
    # 3. Service Agent "Listens" (Decodes)
    # Simulate receiving
    binary_data = bytes.fromhex(hex_data)
    decoded_msg = service_agent.ual.decode(binary_data)
    
    print("\n🤖 Service Bot: Received UAL Packet. Parsing Logic...")
    
    # 4. Service Agent "Thinks" (Process Graph)
    # It doesn't need to parse English again; it traverses the graph directly.
    
    # Logic Engine Simulation
    nodes = decoded_msg.get('nodes', [])
    edges = decoded_msg.get('edges', [])
    
    # Logic Engine Simulation
    has_condition = False
    condition_entity = None
    action = None
    
    # Simple Graph Traversal to find IF-THEN structure
    # Finding Relation=4 (CONDITION) and Relation=5 (CONSEQUENCE)
    
    # Map IDs to Nodes for easy lookup
    node_map = {n.id: n for n in nodes}
    
    for edge in edges:
        if edge.relation == 4: # CONDITION
            if_node = node_map[edge.source_id]
            target_node = node_map[edge.target_id]
            print(f"   [Logic] Detected CONDITION: IF {target_node.str_val} ({target_node.type})")
            
        elif edge.relation == 5: # CONSEQUENCE
            if_node = node_map[edge.source_id]
            target_node = node_map[edge.target_id]
            print(f"   [Logic] Detected CONSEQUENCE: THEN {target_node.str_val} ({target_node.type})")
            
            # Simulated Execution
            print(f"   ✅ Executing Virtual Action: {target_node.str_val}")

    print_separator("Demo Complete")
    print("Conclusion: UAL successfully mediated logic between two software agents without hardware.")

if __name__ == "__main__":
    demo_software_agents()
