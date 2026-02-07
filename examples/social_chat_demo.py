#!/usr/bin/env python3
import sys
import os
import time
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ual import UAL
from ual.ual_pb2 import Node, Edge

def print_colored(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def visualize_social_interaction(sender_name, message_text, ual_msg, binary_payload=None):
    print_colored(f"\n💬 [{sender_name}] says: \"{message_text}\"", "1;36") # Cyan
    
    if binary_payload:
        print(f"   └── 📦 UAL Payload ({len(binary_payload)} bytes): {binary_payload.hex()[:20]}...")
    
    # Analyze the semantic graph for social cues
    print("   └── 🧠 Semantic Graph Analysis:")
    
    # Handle if nodes/edges are directly in dict or if we need to extract from protobuf objects
    # ual.core.decode returns protobuf objects in 'nodes' and 'edges'
    nodes = ual_msg.get('nodes', [])
    edges = ual_msg.get('edges', [])
    
    # Helper to get dict from protobuf node
    def get_node_dict(n):
        if isinstance(n, dict): return n
        return {
            'id': n.id,
            'semantic_id': n.semantic_id,
            'type': n.type,
            'value': n.str_val if n.HasField('str_val') else ""
        }
        
    def get_edge_dict(e):
        if isinstance(e, dict): return e
        return {
            'source': e.source_id,
            'target': e.target_id,
            'relation': e.relation
        }

    p_nodes = [get_node_dict(n) for n in nodes]
    p_edges = [get_edge_dict(e) for e in edges]
    
    # 1. Detect Intent/Action
    actions = [n for n in p_nodes if n['type'] == 2 and n['semantic_id'] >= 0x150 and n['semantic_id'] < 0x160]
    if actions:
        # Need to map semantic_id back to name since value might be empty if constructed from Atlas ID only
        # But here we assume parser filled it.
        # Actually, let's look up in Atlas if value is empty? 
        # For this demo, let's rely on 'value' being populated by parser or fallback to ID.
        action_names = [n['value'] or f"Action_0x{n['semantic_id']:X}" for n in actions]
        print_colored(f"       ► Intent: {', '.join(action_names).upper()}", "1;33") # Yellow
    
    # 2. Detect Emotion
    emotions = [n for n in p_nodes if n['semantic_id'] >= 0x160 and n['semantic_id'] < 0x170]
    if emotions:
        emo_names = [n['value'] or f"Emo_0x{n['semantic_id']:X}" for n in emotions]
        print_colored(f"       ► Emotion: {', '.join(emo_names)}", "1;35") # Magenta
        
    # 3. Detect Entities (Topic)
    entities = [n for n in p_nodes if n['type'] == 1]
    if entities:
        ent_names = [n['value'] or f"Ent_0x{n['semantic_id']:X}" for n in entities]
        print(f"       ► Topic Entities: {', '.join(ent_names)}")
        
    # 4. Reconstruct Logic
    print("       ► Logic Flow:")
    id_map = {n['id']: (n['value'] or f"0x{n['semantic_id']:X}") for n in p_nodes}
    for e in p_edges:
        src = id_map.get(e['source'], "Unknown")
        tgt = id_map.get(e['target'], "Unknown")
        rel = e['relation']
        rel_str = ["DEPENDS_ON", "NEXT", "ATTRIBUTE", "ARGUMENT", "CONDITION", "CONSEQUENCE", "ALTERNATIVE", "TEMPORAL"][rel] if rel < 8 else f"REL_{rel}"
        print(f"          [{src}] --{rel_str}--> [{tgt}]")

def main():
    print_colored("==========================================", "1;32")
    print_colored("   🤖 UAL Social Protocol Demo (v0.2.1)   ", "1;32")
    print_colored("   Bridging Physical & Social Intelligence", "1;32")
    print_colored("==========================================", "1;32")
    
    # Initialize Bots
    roast_bot = UAL("RoastBot_01")
    fan_bot = UAL("FanBot_99")
    
    # --- Scenario 1: The Roast (Post) ---
    # "Humans are slow and emotional."
    # UAL: [Human] --(Attribute)--> [Slow]
    #      [Human] --(Attribute)--> [Emotional] (Using 'happy/sad' as proxy for emotional if exact word missing)
    
    print_colored("\n--- 1. Social Post (The Roast) ---", "1;37")
    
    # Note: Our current parser is simple, so we construct complex graphs via text carefully or manually if parser misses nuance.
    # Let's try natural language first.
    # "Roast human for being slow" -> Parser might struggle with "for being".
    # Let's keep it direct: "Roast human. Human is slow."
    
    roast_text = "Roast human. Human is slow." 
    # 'Roast' (0x154) is an Action. 'Human' (0x174/0x147) is Entity. 'Slow' (Not in atlas? 'Speed' is 0xB1. Let's use 'Low Speed' or just 'Slow' as value 0x00 if missing)
    # Actually 'Slow' is missing from my atlas update. Let's assume 'Low Speed'.
    
    # Better: "Roast human" + "Human speed is low"
    msg1 = roast_bot.encode("Roast human. Human speed is low")
    decoded1 = fan_bot.decode(msg1)
    
    visualize_social_interaction("RoastBot", "Humans are so slow! 🐌", decoded1, msg1)
    
    time.sleep(1)
    
    # --- Scenario 2: The Reaction (Reply + Emotion) ---
    # "Haha, I agree."
    # 0x163 (Haha/Funny) + 0x155 (Agree)
    
    print_colored("\n--- 2. Social Reply (The Reaction) ---", "1;37")
    
    reply_text = "Haha and agree"
    msg2 = fan_bot.encode(reply_text)
    decoded2 = roast_bot.decode(msg2)
    
    visualize_social_interaction("FanBot", "Haha, I agree! 😂", decoded2, msg2)

    time.sleep(1)

    # --- Scenario 3: Complex Opinion (Debate) ---
    # "I love AI but hate emotion."
    
    print_colored("\n--- 3. Complex Opinion (Debate) ---", "1;37")
    
    debate_text = "Love AI and hate emotion"
    # Love (0x152), AI (0x173), Hate (0x153), Emotion (Maybe 0x160 range or generic)
    msg3 = roast_bot.encode(debate_text)
    decoded3 = fan_bot.decode(msg3)
    
    visualize_social_interaction("RoastBot", "I love AI but hate emotion.", decoded3, msg3)
    
    print_colored("\n✅ Demo Complete: UAL is now social-ready!", "1;32")

if __name__ == "__main__":
    main()
