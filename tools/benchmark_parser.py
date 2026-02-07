import time
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from ual.parser import RuleBasedParser, LLMParser
from ual import ual_pb2

def run_benchmark():
    print("🚀 UAL Parser Benchmark")
    print("=======================")
    
    # 1. Setup Parsers
    # Note: LLMParser will fallback to RuleBased if no model is found, 
    # but we can test its auxiliary methods like _get_relevant_concepts
    rb_parser = RuleBasedParser()
    llm_parser = LLMParser(model_path=None) # No model for now
    
    test_cases = [
        # --- Basic Movement ---
        "Move to kitchen",
        "Go to living room",
        "Navigate to zone A",
        "Return to base",
        "Come home",
        
        # --- Action & Object ---
        "Scan target",
        "Scan area",
        "Look for keys",
        "Find obstacle",
        "Take package from shelf",
        "Pick pallet from rack",
        "Drop cargo here",
        "Place item on table",
        
        # --- Compound / Sequence ---
        "Scan area and return to base",
        "Pick item and place on conveyor",
        "Go to kitchen then find water",
        "Take sample and analyze",
        
        # --- High Priority / Safety ---
        "Stop immediately",
        "Emergency stop",
        "Hover now",
        "Do not move",
        "Never fly there",
        
        # --- Conditionals (Best for LLM) ---
        "If obstacle then stop",
        "If battery low then return",
        "If door open then wait",
        
        # --- Numeric / EnvFrame ---
        "Hover at 10, 20, 5",
        "Fly to 100, 200",
        "Set speed to 5",
        
        # --- Abstract / Query ---
        "Uncertainty is high",
        "Battery check",
        "Status report",
        "All drones return"
    ]
    
    print(f"\nrunning {len(test_cases)} test cases (RuleBased vs LLM-Helper)...\n")
    
    results = []
    
    for text in test_cases:
        print(f"Input: \"{text}\"")
        
        # Test RuleBased
        start = time.time()
        nodes, edges, meta = rb_parser.parse(text)
        duration = (time.time() - start) * 1000
        
        print(f"  [RuleBased] {duration:.2f}ms | Nodes: {len(nodes)} | Edges: {len(edges)} | Urgency: {meta.get('urgency', 0)}")
        
        # Verify specific logic for RuleBased
        if "not" in text:
            has_not = any(n.semantic_id == 0xC1 for n in nodes)
            print(f"    -> Negation Detected: {has_not}")
        
        if "and" in text:
             # Check for sequence
             has_next = any(e.relation == 1 for e in edges)
             print(f"    -> Sequence Detected: {has_next}")
             
        # Test LLM Helper (Relevant Concepts)
        concepts = llm_parser._get_relevant_concepts(text)
        concept_count = len(concepts.split('\n'))
        print(f"  [LLM Helper] Relevant Concepts: {concept_count}")
        # print(f"    -> {concepts}")
        
        print("-" * 40)

if __name__ == "__main__":
    run_benchmark()
