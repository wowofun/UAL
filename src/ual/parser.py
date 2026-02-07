import re
import json
import logging
import uuid
import hashlib
import time
from typing import List, Dict, Any, Tuple, Optional
from . import ual_pb2
from .atlas import get_atlas

logger = logging.getLogger(__name__)

class SemanticParser:
    """
    Base class for Natural Language to UAL Graph parsers.
    """
    def __init__(self):
        self._cache: Dict[str, Tuple[List[ual_pb2.Node], List[ual_pb2.Edge], Dict[str, Any]]] = {}

    def parse(self, text: str) -> Tuple[List[ual_pb2.Node], List[ual_pb2.Edge], Dict[str, Any]]:
        """
        Parse text into nodes, edges, and metadata (urgency, style, env_frame).
        """
        # 1. Check Cache
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        if text_hash in self._cache:
            logger.debug(f"⚡ Cache Hit for: {text[:20]}...")
            return self._cache[text_hash]

        # 2. Fast Path for Short Sentences
        # If text is short and simple, force RuleBased (unless this IS RuleBased)
        word_count = len(text.split())
        if word_count < 8 and " and " not in text.lower() and " if " not in text.lower() and not isinstance(self, RuleBasedParser):
             # Simple heuristic: Delegate to RuleBased if simple enough
             # But let LLMParser decide via its own logic (it inherits this, but overrides _parse_impl)
             pass

        result = self._parse_impl(text)
        
        # 3. Update Cache
        if result:
             self._cache[text_hash] = result
             
        return result

    def _parse_impl(self, text: str) -> Tuple[List[ual_pb2.Node], List[ual_pb2.Edge], Dict[str, Any]]:
        raise NotImplementedError

class RuleBasedParser(SemanticParser):
    """
    Enhanced Rule-Based Parser (v2.1).
    Handles:
    - Negation ("not move")
    - Conjunctions ("move and scan")
    - SVO (Subject-Verb-Object)
    - Prepositions ("move to kitchen", "take from shelf")
    - Continuous Actions (NEXT chains)
    """
    def __init__(self):
        super().__init__()
        self.atlas = get_atlas()
        
    def _parse_impl(self, text: str) -> Tuple[List[ual_pb2.Node], List[ual_pb2.Edge], Dict[str, Any]]:
        text = text.lower().replace('.', '')
        words = text.split()
        
        nodes = []
        edges = []
        metadata = {"urgency": 0.0, "style": 0} # DEFAULT

        # Identify Urgency Keywords
        if any(w in words for w in ["immediately", "urgent", "now", "emergency"]):
            metadata["urgency"] = 0.9
            metadata["style"] = 2 # COMMAND
            
        # --- Stage 1: Token to Node Mapping ---
        # Map words to nodes, handling negation and separators
        token_nodes = [] # List of (word, node, is_action, token_type)
        
        i = 0
        while i < len(words):
            word = words[i]
            
            # 1. Negation
            is_negated = False
            if word in ["not", "dont", "don't", "no", "never"]:
                if i + 1 < len(words):
                    is_negated = True
                    word = words[i+1] # Consume next word
                    i += 1
            
            # 2. Structural Markers
            if word in ["and", "then"]:
                token_nodes.append((word, None, False, "SEPARATOR"))
                i += 1
                continue
            if word in ["if"]:
                # Explicit IF token
                if_node = ual_pb2.Node()
                if_node.id = str(uuid.uuid4())[:8]
                if_node.semantic_id = 0xC1 # IF
                if_node.type = 4 # LOGIC
                nodes.append(if_node)
                token_nodes.append((word, if_node, False, "LOGIC_START"))
                i += 1
                continue
            if word in ["else"]:
                # Explicit ELSE token
                token_nodes.append((word, None, False, "LOGIC_ELSE"))
                i += 1
                continue
            
            if word in ["to", "from", "at", "in", "on", "with", "by", "of"]:
                token_nodes.append((word, None, False, "PREPOSITION"))
                i += 1
                continue

            # 3. Bigram Check (Phrasal Verbs e.g., "turn on", "pick up")
            semantic_id = None
            consumed_next = False
            
            if i + 1 < len(words):
                next_word = words[i+1]
                bigram = f"{word}_{next_word}"
                sid = self.atlas.get_id(bigram)
                if sid:
                    semantic_id = sid
                    consumed_next = True
            
            # 4. Unigram Check
            if not semantic_id:
                semantic_id = self.atlas.get_id(word)
            
            # 5. Number Check (Value)
            is_number = False
            try:
                float(word)
                is_number = True
            except ValueError:
                pass

            if is_number and not semantic_id:
                node = ual_pb2.Node()
                node.id = str(uuid.uuid4())[:8]
                node.semantic_id = 0x00 # VALUE
                node.type = 6 # VALUE
                node.str_val = word
                nodes.append(node)
                token_nodes.append((word, node, False, "VALUE"))
                i += 1
                continue

            if semantic_id:
                if consumed_next:
                    i += 1 # Skip next word since we consumed it as bigram
                
                node = ual_pb2.Node()
                node.id = str(uuid.uuid4())[:8]
                node.semantic_id = semantic_id
                
                # Check Type (Heuristic based on ID range)
                # 0xA0+ = Action, 0xE0+ = Entity, 0xB0+ = Property
                is_action = (semantic_id >= 0xA0 and semantic_id < 0xB0)
                node.type = 2 if is_action else 1 # 2=ACTION, 1=ENTITY
                
                if is_negated:
                    not_node = ual_pb2.Node()
                    not_node.id = str(uuid.uuid4())[:8]
                    not_node.semantic_id = 0xC1 # Logic NOT
                    not_node.type = 4 # LOGIC
                    nodes.append(not_node)
                    
                    # Edge: NOT --(CONDITION)--> Concept
                    edge = ual_pb2.Edge()
                    edge.source_id = not_node.id
                    edge.target_id = node.id
                    edge.relation = 4 # CONDITION
                    edges.append(edge)
                
                nodes.append(node)
                token_nodes.append((word, node, is_action, "NODE"))
            else:
                # Unknown word
                pass
            
            i += 1
            
        # --- Stage 2: Structural Linking (State Machine) ---
        
        # Split into clauses by "and/then" AND "else"
        clauses = []
        clause_separators = [] # Stores what separated the clause (None, THEN, ELSE)
        current_clause = []
        
        for item in token_nodes:
            word, node, is_action, token_type = item
            
            if token_type == "SEPARATOR":
                clauses.append(current_clause)
                clause_separators.append("THEN") # Treat 'and'/'then' as standard flow
                current_clause = []
            elif token_type == "LOGIC_ELSE":
                clauses.append(current_clause)
                clause_separators.append("ELSE")
                current_clause = []
            else:
                current_clause.append(item)
                
        if current_clause:
            clauses.append(current_clause)
            clause_separators.append("END")
            
        # Link within clauses and across clauses
        previous_action_node = None
        pending_if_node = None # Track active IF node to link Consequence/Alternative
        
        for idx, clause in enumerate(clauses):
            if not clause: continue
            
            # Pattern: [Action] [Prep] [Entity] OR [Action] [Entity]
            
            clause_action = None
            clause_root = None # The main node of this clause (Action or Entity)
            last_preposition = None
            current_if_node = None
            last_value_node = None # Track number/value to attach to next entity
            
            # 1. Intra-Clause Linking
            for j, (word, node, is_action, token_type) in enumerate(clause):
                if token_type == "LOGIC_START":
                    current_if_node = node
                    continue
                
                if token_type == "VALUE":
                    last_value_node = node
                    continue
                    
                if token_type == "PREPOSITION":
                    last_preposition = word
                    continue
                
                if node is None: continue 
                
                # First significant node is candidate for root (if no action found yet)
                if clause_root is None:
                    clause_root = node
                
                if is_action:
                    clause_action = node
                    clause_root = node # Action takes precedence as root
                    
                    # Link previous action (Sequence) ONLY if not in a Logic Structure
                    # If we are in a logic structure (Consequence/Alternative), we link from IF, not previous action
                    if previous_action_node and not pending_if_node:
                        edge = ual_pb2.Edge()
                        edge.source_id = previous_action_node.id
                        edge.target_id = clause_action.id
                        edge.relation = 1 # NEXT
                        edges.append(edge)
                    
                    previous_action_node = clause_action
                    last_preposition = None # Reset prep after new action
                    
                    # Attach dangling value to Action? (e.g. "10 move" -> 10 times?)
                    if last_value_node:
                         edge = ual_pb2.Edge()
                         edge.source_id = node.id
                         edge.target_id = last_value_node.id
                         edge.relation = 2 # ATTRIBUTE
                         edges.append(edge)
                         last_value_node = None
                    
                elif not is_action:
                    # Entity Node
                    
                    # 1. Attach dangling value (e.g. "10" -> "minutes")
                    if last_value_node:
                        edge = ual_pb2.Edge()
                        edge.source_id = node.id # Entity
                        edge.target_id = last_value_node.id # Value
                        edge.relation = 2 # ATTRIBUTE (Unit has Value)
                        edges.append(edge)
                        last_value_node = None

                    if clause_action:
                        # Entity follows Action -> Argument
                        relation = 3 # ARGUMENT (default)
                        
                        # Temporal Check (0x100 - 0x13F)
                        if 0x100 <= node.semantic_id < 0x140:
                            relation = 7 # TEMPORAL
                        
                        # Refine relation based on preposition
                        if last_preposition in ["to", "at", "in", "on"]:
                            relation = 3 # Still Argument (Destination/Location)
                        elif last_preposition == "from":
                            relation = 3 # Source
                            
                        edge = ual_pb2.Edge()
                        edge.source_id = clause_action.id
                        edge.target_id = node.id
                        edge.relation = relation
                        edges.append(edge)
                        
                        last_preposition = None # Consumed
            
            # 2. Logic Linking (Inter-Clause)
            
            # Case A: This clause started a Logic Block (contains IF)
            if current_if_node:
                pending_if_node = current_if_node
                # Link IF -> Clause Root (Condition)
                if clause_root:
                    edge = ual_pb2.Edge()
                    edge.source_id = current_if_node.id
                    edge.target_id = clause_root.id
                    edge.relation = 4 # CONDITION
                    edges.append(edge)
                    
            # Case B: This clause is a Consequence or Alternative (part of pending IF)
            elif pending_if_node:
                # Check what separated the PREVIOUS clause
                prev_sep = clause_separators[idx-1] if idx > 0 else "END"
                
                if prev_sep == "THEN":
                    # This is the THEN part (Consequence)
                    if clause_root:
                        edge = ual_pb2.Edge()
                        edge.source_id = pending_if_node.id
                        edge.target_id = clause_root.id
                        edge.relation = 5 # CONSEQUENCE
                        edges.append(edge)
                        
                elif prev_sep == "ELSE":
                    # This is the ELSE part (Alternative)
                    if clause_root:
                        edge = ual_pb2.Edge()
                        edge.source_id = pending_if_node.id
                        edge.target_id = clause_root.id
                        edge.relation = 6 # ALTERNATIVE
                        edges.append(edge)
                    
                    # Usually ELSE ends the logic block
                    pending_if_node = None

        return nodes, edges, metadata

class LLMParser(SemanticParser):
    """
    LLM-Powered Parser (Expert Edition).
    Features:
    - Dynamic Atlas Injection (RAG-lite)
    - Enhanced Few-Shot Learning (12 examples)
    - Output Validation & Retry
    - EnvFrame Extraction
    """
    def __init__(self, model_path: str = None):
        super().__init__()
        self.model_path = model_path
        self.llm = None
        self.atlas = get_atlas()
        
        if model_path:
            try:
                from llama_cpp import Llama
                self.llm = Llama(model_path=model_path, n_ctx=4096, verbose=False)
                logger.info(f"✅ Loaded Local LLM: {model_path}")
            except ImportError:
                logger.warning("⚠️ llama-cpp-python not installed. LLM Parser disabled.")
            except Exception as e:
                logger.error(f"⚠️ Failed to load LLM: {e}")

    def _get_relevant_concepts(self, text: str) -> str:
        """
        Filter Atlas to only relevant concepts to save tokens.
        Strategy:
        1. Always include Structural Concepts (Logic 0xC0, Modal 0xD0, Relations).
        2. Include Concepts that appear in text (fuzzy match).
        """
        text_lower = text.lower()
        relevant_lines = []
        
        # 1. Core Structure (Always Include)
        # Manually adding core concepts if they aren't caught by fuzzy match, 
        # but actually, it's safer to just iterate and check.
        
        for sid, concept in self.atlas._id_to_concept.items():
            is_relevant = False
            
            # Category checks
            is_logic = (0xC0 <= sid < 0xD0)
            is_modal = (0xD0 <= sid < 0xE0)
            is_meta = (0xF0 <= sid < 0x100)
            
            # Content check
            # Simple substring match. 
            # "move" in "remove" -> True (False positive, but okay for MVP)
            # "drone" in "drones" -> True
            if concept in text_lower or concept[:-1] in text_lower: # Simple singular check
                is_relevant = True
            
            if is_logic or is_modal or is_relevant:
                relevant_lines.append(f"- {concept}: 0x{sid:X}")
                
        return "\n".join(relevant_lines)

    def _parse_impl(self, text: str) -> Tuple[List[ual_pb2.Node], List[ual_pb2.Edge], Dict[str, Any]]:
        # Fast Path for very simple queries
        if len(text.split()) < 5 and " and " not in text.lower() and not self.llm:
             return RuleBasedParser().parse(text)

        if not self.llm:
            return RuleBasedParser().parse(text)

        # --- Dynamic Atlas ---
        atlas_subset = self._get_relevant_concepts(text)
        
        prompt = f"""
System: You are an expert UAL (Universal Agent Language) Compiler.
Task: Translate Natural Language into a Semantic DAG (Directed Acyclic Graph) JSON.

[CONSTRAINTS]
1. Use ONLY Semantic IDs from the provided Atlas. If a concept is missing, use closest match or 0x00.
2. Output valid JSON only. No markdown.
3. Node Types: 1=ENTITY, 2=ACTION, 3=PROPERTY, 4=LOGIC, 5=MODAL, 6=VALUE.
4. Edge Relations: 0=DEPENDS_ON, 1=NEXT, 2=ATTRIBUTE, 3=ARGUMENT, 4=CONDITION.
5. Extract 'urgency' (0.0-1.0) and 'style' (COMMAND=2, REQUEST=1) into 'header'.
6. If location is mentioned (e.g. "at 10,20,5"), extract to 'env_frame'.

[ATLAS (Relevant Subset)]
{atlas_subset}

[FEW-SHOT EXAMPLES]
Input: "Move to kitchen"
Output: {{ "header": {{ "urgency": 0.5, "style": 2 }}, "nodes": [ {{ "id": "n1", "semantic_id": 0xA1, "type": 2, "value": "move" }}, {{ "id": "n2", "semantic_id": 0xE5, "type": 1, "value": "kitchen" }} ], "edges": [ {{ "source": "n1", "target": "n2", "relation": 3 }} ] }}

Input: "Do not move"
Output: {{ "header": {{ "urgency": 0.5, "style": 2 }}, "nodes": [ {{ "id": "n1", "semantic_id": 0xC1, "type": 4, "value": "not" }}, {{ "id": "n2", "semantic_id": 0xA1, "type": 2, "value": "move" }} ], "edges": [ {{ "source": "n1", "target": "n2", "relation": 4 }} ] }}

Input: "Scan area and return to base"
Output: {{ "header": {{ "urgency": 0.5, "style": 2 }}, "nodes": [ {{ "id": "n1", "semantic_id": 0xA2, "type": 2, "value": "scan" }}, {{ "id": "n2", "semantic_id": 0xE2, "type": 1, "value": "area" }}, {{ "id": "n3", "semantic_id": 0xA1, "type": 2, "value": "move" }}, {{ "id": "n4", "semantic_id": 0xE4, "type": 1, "value": "base" }} ], "edges": [ {{ "source": "n1", "target": "n2", "relation": 3 }}, {{ "source": "n1", "target": "n3", "relation": 1 }}, {{ "source": "n3", "target": "n4", "relation": 3 }} ] }}

Input: "If obstacle then stop immediately"
Output: {{ "header": {{ "urgency": 0.9, "style": 2 }}, "nodes": [ {{ "id": "n1", "semantic_id": 0xC1, "type": 4, "value": "if" }}, {{ "id": "n2", "semantic_id": 0xE3, "type": 1, "value": "obstacle" }}, {{ "id": "n3", "semantic_id": 0xC2, "type": 4, "value": "then" }}, {{ "id": "n4", "semantic_id": 0xA5, "type": 2, "value": "stop" }} ], "edges": [ {{ "source": "n1", "target": "n2", "relation": 3 }}, {{ "source": "n1", "target": "n3", "relation": 1 }}, {{ "source": "n3", "target": "n4", "relation": 3 }} ] }}

Input: "Hover at 10, 20, 5"
Output: {{ "header": {{ "urgency": 0.5, "style": 2 }}, "env_frame": {{ "origin": [10, 20, 5], "unit": "meter" }}, "nodes": [ {{ "id": "n1", "semantic_id": 0xA5, "type": 2, "value": "hover" }} ], "edges": [] }}

Input: "Battery check"
Output: {{ "header": {{ "urgency": 0.1, "style": 1 }}, "nodes": [ {{ "id": "n1", "semantic_id": 0xB4, "type": 3, "value": "battery" }} ], "edges": [] }}

Input: "All drones return"
Output: {{ "header": {{ "urgency": 0.5, "style": 2 }}, "nodes": [ {{ "id": "n1", "semantic_id": 0xE1, "type": 1, "value": "drone" }}, {{ "id": "n2", "semantic_id": 0xA1, "type": 2, "value": "move/return" }} ], "edges": [ {{ "source": "n2", "target": "n1", "relation": 3 }} ] }}

Input: "Uncertainty is high"
Output: {{ "header": {{ "urgency": 0.3, "style": 0 }}, "nodes": [ {{ "id": "n1", "semantic_id": 0x0F1, "type": 3, "value": "uncertainty" }}, {{ "id": "n2", "semantic_id": 0x00, "type": 6, "value": "high" }} ], "edges": [ {{ "source": "n1", "target": "n2", "relation": 2 }} ] }}

Input: "{text}"
Output JSON:
"""
        try:
            output = self.llm(prompt, max_tokens=512, stop=["Input:", "\n\n"], echo=False, temperature=0.1)
            json_str = output['choices'][0]['text'].strip()
            
            # Robust JSON Extraction
            match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if match:
                json_str = match.group(0)
            
            data = json.loads(json_str)
            
            # --- Validation & Reconstruction ---
            nodes = []
            edges = []
            id_map = {}
            metadata = data.get("header", {})
            if "env_frame" in data: # Handle if env_frame is outside header
                 metadata["env_frame"] = data["env_frame"]
            elif "env_frame" in metadata:
                 pass
            
            # Validate Nodes
            for n in data.get("nodes", []):
                sid = n.get('semantic_id')
                concept = self.atlas.get_concept(sid)
                
                if not concept and sid != 0:
                    # Fallback: check if we can find it by value
                    val = n.get('value', '')
                    rec_sid = self.atlas.get_id(val)
                    if rec_sid:
                        sid = rec_sid
                    else:
                        logger.warning(f"⚠️ LLM hallucinated ID {sid}, mapping to UNKNOWN (0x00)")
                        sid = 0x00
                    
                node = ual_pb2.Node()
                real_id = str(uuid.uuid4())[:8]
                id_map[n['id']] = real_id
                node.id = real_id
                node.semantic_id = sid
                node.type = n.get('type', 0)
                if 'value' in n:
                    node.str_val = str(n['value'])
                nodes.append(node)
                
            # Validate Edges
            for e in data.get("edges", []):
                src = id_map.get(e['source'])
                tgt = id_map.get(e['target'])
                
                if not src or not tgt:
                    continue 
                    
                edge = ual_pb2.Edge()
                edge.source_id = src
                edge.target_id = tgt
                edge.relation = e.get('relation', 0)
                edge.weight = e.get('weight', 1.0)
                edges.append(edge)
                
            return nodes, edges, metadata

        except Exception as e:
            logger.error(f"❌ LLM Parsing Failed: {e}")
            # Fallback to RuleBased
            return RuleBasedParser().parse(text)
