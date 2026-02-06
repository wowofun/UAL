import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from ual import UAL
from ual.ual_pb2 import Header, EnvironmentalFrame, Edge
from ual.primitives import SemanticPrime, PrimitiveBuilder
from ual.translator import AutoTranslator

def main():
    print("=== UAL Phase 4: Generalization Demo ===\n")
    
    # 1. Initialize
    agent_a = UAL("Agent_A")
    translator = AutoTranslator(agent_a.atlas)
    
    # --- Feature 1: Recursive Semantic Primitives (Zero-shot) ---
    print("--- 1. Recursive Semantic Primitives (Zero-shot) ---")
    # Define "Refuse" = I + WANT + NOT + DO
    refuse_def = PrimitiveBuilder.define_concept(
        "Refuse", 
        agent_a,
        [
            (SemanticPrime.I, Edge.ARGUMENT),
            (SemanticPrime.WANT, Edge.NEXT),
            (SemanticPrime.NOT, Edge.ATTRIBUTE),
            (SemanticPrime.DO, Edge.ARGUMENT)
        ]
    )
    print(f"Defined 'Refuse' using {len(refuse_def.nodes)} primitive nodes.")
    print(f"Structure: I -> WANT -(not)-> DO")
    
    # --- Feature 2: Environmental Frame ---
    print("\n--- 2. World-State Resonance (Env Frame) ---")
    # Create a message with spatial context
    msg_header = Header()
    msg_header.sender_id = "Agent_A"
    msg_header.timestamp = int(time.time())
    
    # Attach Env Frame
    frame = EnvironmentalFrame()
    frame.frame_id = "local_base_link"
    frame.origin.extend([10.5, 20.2, 0.0])
    frame.orientation.extend([0.0, 0.0, 0.0, 1.0])
    frame.unit = "meter"
    
    msg_header.env_frame.CopyFrom(frame)
    print(f"Attached Env Frame: {frame.frame_id} at {frame.origin}")
    
    # --- Feature 3: Sentiment & Priority ---
    print("\n--- 3. Sentiment & Priority Vectors ---")
    msg_header.urgency = 0.95 # Critical
    msg_header.style = Header.COMMAND
    print(f"Urgency: {msg_header.urgency}")
    print(f"Style: COMMAND ({msg_header.style})")
    
    # --- Feature 4: Auto-Translator (Self-Evolution) ---
    print("\n--- 4. Auto-Translator (Self-Evolution) ---")
    unknown_term = "Collaborate"
    
    # Try to resolve locally
    id_local = agent_a.atlas.get_id(unknown_term)
    print(f"Local lookup for '{unknown_term}': {id_local}")
    
    if not id_local:
        # Use Translator
        graph = translator.translate(unknown_term)
        if graph:
            # Now verify it's learned
            new_id = agent_a.atlas.get_id(unknown_term) # Note: get_id needs update to check dynamic registry by name? 
            # atlas.get_id currently only checks active namespaces for reverse lookup?
            # Let's check the dynamic registry directly for demo
            
            # Find ID by value in dynamic registry
            found_id = None
            for k, v in agent_a.atlas._dynamic_registry.items():
                if v == unknown_term:
                    found_id = k
                    break
            
            print(f"Translator learned '{unknown_term}' -> Dynamic ID {hex(found_id) if found_id else 'None'}")
            
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
