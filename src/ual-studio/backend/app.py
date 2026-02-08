import sys
import os
import time
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../.env'))

# Add UAL source to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ual.atlas import UniversalAtlas
from ual.core import UAL
from ual import ual_pb2

app = Flask(__name__)
CORS(app)

atlas = UniversalAtlas()
core = UAL(agent_id="studio_backend")

# Initialize some mock state
core.tracker.update("battery", 100.0)
core.tracker.update("position", [0.0, 0.0, 0.0])
core.tracker.update("status", "idle")

def get_category(sem_id):
    if 0x0A0 <= sem_id < 0x0B0: return "Action"
    if 0x0B0 <= sem_id < 0x0C0: return "Property"
    if 0x0C0 <= sem_id < 0x0D0: return "Logic"
    if 0x0D0 <= sem_id < 0x0E0: return "Modal"
    if 0x0E0 <= sem_id < 0x0F0: return "Entity"
    if 0x0F0 <= sem_id < 0x100: return "Meta"
    if 0x150 <= sem_id < 0x180: return "Social"
    if sem_id >= 0x1000: return "Custom"
    return "Unknown"

@app.route('/api/atlas', methods=['GET'])
def get_atlas():
    concepts = []
    for sem_id, name in atlas._id_to_concept.items():
        category = get_category(sem_id)
        concepts.append({
            "id": sem_id,
            "name": name,
            "category": category,
            "hex": f"0x{sem_id:03X}"
        })
    
    for ns in atlas._active_namespaces:
        if ns in atlas._namespaces:
            for sem_id, name in atlas._namespaces[ns].items():
                concepts.append({
                    "id": sem_id,
                    "name": name,
                    "category": f"Ext:{ns}",
                    "hex": f"0x{sem_id:03X}"
                })
                
    return jsonify(concepts)

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Return current drone state (mocked or real).
    """
    # Simulate battery drain
    current_bat = core.tracker.get("battery") or 100.0
    if current_bat > 0:
        core.tracker.update("battery", max(0, current_bat - 0.05))
        
    return jsonify(core.tracker.state)

@app.route('/api/parse', methods=['POST'])
def parse_graph():
    """
    Parse a JSON representation of the graph (from ReactFlow) into UAL
    and simulate execution.
    """
    data = request.json
    nodes_data = data.get('nodes', [])
    edges_data = data.get('edges', [])
    
    # 1. Convert to UAL Protobuf
    ual_nodes = []
    ual_edges = []
    
    node_map = {} # ReactFlow ID -> UAL Node
    
    for n in nodes_data:
        sem_id = n.get('semantic_id')
        node_name = n.get('name', 'unknown')
        
        # Determine Type based on Semantic ID range
        node_type = ual_pb2.Node.UNKNOWN
        cat = get_category(sem_id)
        if cat == "Action": node_type = ual_pb2.Node.ACTION
        elif cat == "Entity": node_type = ual_pb2.Node.ENTITY
        elif cat == "Property": node_type = ual_pb2.Node.PROPERTY
        elif cat == "Logic": node_type = ual_pb2.Node.LOGIC
        elif cat == "Value": node_type = ual_pb2.Node.VALUE
        
        # Create Node
        ual_node = core.create_node(node_type, semantic_id=sem_id, id=n['id'])
        ual_node.str_val = node_name # Store debug name
        ual_nodes.append(ual_node)
        node_map[n['id']] = ual_node

    for e in edges_data:
        # Simple relation mapping for now
        ual_edge = core.create_edge(e['source'], e['target'], ual_pb2.Edge.NEXT)
        ual_edges.append(ual_edge)

    graph = core.create_graph(ual_nodes, ual_edges, context_id="studio_exec")
    
    # 2. Simulate Execution (Simple Interpreter)
    # Find Action Nodes and "execute" them
    executed_actions = []
    
    for node in ual_nodes:
        if node.type == ual_pb2.Node.ACTION:
            action_name = atlas.get_concept(node.semantic_id)
            executed_actions.append(action_name)
            
            # Update State based on Action
            if action_name == "move":
                core.tracker.update("status", "moving")
                curr_pos = core.tracker.get("position") or [0,0,0]
                # Random move
                new_pos = [curr_pos[0] + random.uniform(-1,1), curr_pos[1] + random.uniform(-1,1), curr_pos[2]]
                core.tracker.update("position", new_pos)
            elif action_name == "hover":
                core.tracker.update("status", "hovering")
            elif action_name == "scan":
                core.tracker.update("status", "scanning")
            elif action_name == "return":
                core.tracker.update("status", "returning")
                core.tracker.update("position", [0.0, 0.0, 0.0])

    if not executed_actions:
        return jsonify({
            "status": "success", 
            "message": "No executable actions found in the graph.",
            "node_count": len(ual_nodes)
        })

    return jsonify({
        "status": "success", 
        "message": f"Executed: {', '.join(executed_actions)}",
        "node_count": len(ual_nodes)
    })

from ual.llm_client import LLMClient
llm_client = LLMClient()

# ... existing code ...

@app.route('/api/generate', methods=['POST'])
def generate_graph():
    """
    AI Assist: Convert natural language to ReactFlow graph JSON.
    """
    text = request.json.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    # [Auto-Translation] Support multi-language input
    # If the user inputs non-English text (e.g., Chinese), translate it to English
    # so the LLM/Compiler can process it using the standard Atlas.
    original_text = text
    try:
        # 'auto' detection is robust for major languages like zh-CN, es, fr, etc.
        translator = GoogleTranslator(source='auto', target='en')
        translated_text = translator.translate(text)
        
        if translated_text and translated_text.lower() != text.lower():
            print(f"🌍 [Translation] '{text}' -> '{translated_text}'")
            text = translated_text
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        # Fallback to original text if translation API fails
        
    # Get Atlas Concepts for LLM Context
    concepts = []
    for sem_id, name in atlas._id_to_concept.items():
        concepts.append({
            "id": sem_id,
            "name": name,
            "category": get_category(sem_id),
            "hex": f"0x{sem_id:03X}"
        })

    # Use LLM Client
    result = llm_client.generate_ual_graph(text, concepts)
    
    # Post-process to add positions (Layout)
    nodes = result.get('nodes', [])
    edges = result.get('edges', [])
    
    x_pos = 100
    y_pos = 100
    
    for i, node in enumerate(nodes):
        if 'position' not in node:
            node['position'] = {"x": x_pos, "y": y_pos}
            x_pos += 200
        
        # Ensure data structure matches what Frontend expects
        if 'data' not in node:
            node['data'] = {
                "label": node.get('name', 'Unknown'),
                "ual": {
                    "id": node.get('semantic_id', 0),
                    "name": node.get('name', 'Unknown'),
                    "category": node.get('category', 'Entity'),
                    "hex": node.get('hex', '0x000')
                }
            }
            
        # Ensure ID
        if 'id' not in node:
            node['id'] = f"gen_node_{i}"

    return jsonify({
        "nodes": nodes,
        "edges": edges
    })


def get_color_for_cat(category):
    if category == 'Action': return '#ffefd5'
    if category == 'Entity': return '#e0ffff'
    if category == 'Property': return '#e6e6fa'
    if category == 'Logic': return '#ffe4e1'
    return '#fff'

if __name__ == '__main__':
    app.run(debug=True, port=5001)
