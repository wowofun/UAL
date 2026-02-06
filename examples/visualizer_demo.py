import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from ual import UAL
from ual.visualizer import UALVisualizer
from ual.ual_pb2 import Node, Edge

def main():
    print("=== UAL Visualization & Uncertainty Demo ===\n")

    # 1. Initialize Agents
    observer = UAL("Observer_Drone")
    
    # 2. Simulate a scenario: "I see an object at (10, 20). 70% Fire, 30% Reflection."
    # Build Graph Manually for fine-grained control
    
    # Node 1: The Unknown Object
    obj_node = observer.create_node(
        node_type=Node.ENTITY,
        semantic_id=0x0E3, # Obstacle/Object (using obstacle as proxy)
        id="obj_01"
    )
    
    # Node 2: Position Value
    pos_node = observer.create_node(
        node_type=Node.VALUE,
        value="10, 20, 5",
        id="pos_val"
    )
    
    # Node 3: Fire Concept (using 'target' as proxy or dynamic)
    # Let's use a dynamic concept for "Fire"
    observer.atlas._dynamic_registry[0x3001] = "Fire"
    fire_node = observer.create_node(
        node_type=Node.ENTITY,
        semantic_id=0x3001,
        id="fire_concept"
    )
    
    # Node 4: Reflection Concept
    observer.atlas._dynamic_registry[0x3002] = "Reflection"
    refl_node = observer.create_node(
        node_type=Node.ENTITY,
        semantic_id=0x3002,
        id="refl_concept"
    )
    
    # Edges
    # Object has Position
    # Using helper methods from UAL core
    e1 = observer.create_edge("obj_01", "pos_val", Edge.ATTRIBUTE)
    
    # Object IS Fire (70% confidence)
    e2 = observer.create_edge("obj_01", "fire_concept", Edge.ATTRIBUTE, weight=0.7)
    
    # Object IS Reflection (30% confidence)
    e3 = observer.create_edge("obj_01", "refl_concept", Edge.ATTRIBUTE, weight=0.3)
    
    # Build Graph
    graph = observer.create_graph(
        nodes=[obj_node, pos_node, fire_node, refl_node],
        edges=[e1, e2, e3]
    )
    
    print(f"Graph Created: {len(graph.nodes)} nodes, {len(graph.edges)} edges.")
    print("Edge 2 (Fire): Confidence = 70%")
    print("Edge 3 (Refl): Confidence = 30%")
    
    # 3. Visualize
    print("\nGenerating Visualization...")
    vis = UALVisualizer(atlas=observer.atlas)
    
    output_path = "uncertainty_demo.png"
    vis.visualize(graph, title="Drone Perception: Uncertainty Cloud", output_file=output_path)
    
    if os.path.exists(output_path):
        print(f"Success! Visualization saved to: {os.path.abspath(output_path)}")
    else:
        print("Visualization failed (Matplotlib missing?).")

if __name__ == "__main__":
    main()
