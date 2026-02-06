import sys
import os
import time
import random

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ual import UAL, get_atlas

def simulate_network_delay():
    time.sleep(0.5)

class DroneAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.ual = UAL(agent_id=agent_id)
        self.role = "Leader" if "A" in agent_id else "Follower"
        print(f"[{self.agent_id}] Online. Role: {self.role}")

    def send(self, message: str, receiver: 'DroneAgent'):
        print(f"\n[{self.agent_id}] Thinking: '{message}'")
        
        # Encode
        binary = self.ual.encode(message, receiver_id=receiver.agent_id)
        print(f"[{self.agent_id}] Transmitting {len(binary)} bytes UAL packet...")
        
        simulate_network_delay()
        
        # Receiver receives
        receiver.receive(binary)

    def receive(self, binary_data: bytes):
        # Decode
        result = self.ual.decode(binary_data)
        
        sender = result['sender']
        meaning = result['natural_language']
        
        print(f"[{self.agent_id}] Received from {sender}:")
        print(f"    > Decoded Meaning: {meaning}")
        print(f"    > Semantic Hash: {result['semantic_hash']}")
        
        # React logic (Mock)
        self.react(meaning, sender)

    def react(self, meaning: str, sender_id: str):
        # Simple state machine based on keywords
        if "scan" in meaning and "target" in meaning:
            response = "Target confirmed. I move to position."
            # In a real loop, we would trigger send here, but to avoid infinite recursion in this simple script,
            # we'll handle the flow in main() or use a flag.
            pass
        elif "move" in meaning:
            pass

def main():
    print("=== UAL Drone Collaboration Demo ===\n")
    
    drone_a = DroneAgent("Drone_A")
    drone_b = DroneAgent("Drone_B")
    
    # Scene 1: Handshake (Mocked via NL for now)
    # 实际协议中会有专门的 Handshake 消息
    print("\n--- Phase 1: Coordination ---")
    
    # Drone A initiates Handshake
    print(f"[Drone_A] Initiating Handshake...")
    handshake_bytes = drone_a.ual.create_handshake(capabilities=["move", "grab"], compute_power=80)
    drone_b.receive(handshake_bytes)

    # Drone B acknowledges (via NL for simplicity or another handshake)
    drone_a.send("Status check. Battery level high.", drone_b)
    
    # Scene 2: Mission Start
    print("\n--- Phase 2: Mission Execution ---")
    # Drone A finds target
    drone_a.send("Scan found Target at Position.", drone_b)
    
    # Drone B responds
    drone_b.send("I Must Move to Position.", drone_a)
    
    # Drone A actions
    drone_a.send("I will Grab Package.", drone_b)
    
    # Drone B confirms
    drone_b.send("Status Normal. I Hover.", drone_a)
    
    print("\n=== Mission Complete ===")

if __name__ == "__main__":
    main()
