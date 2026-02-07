import os
import json
import logging
from typing import Dict, Any, List, Optional

# Try importing openai, handle if not installed
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("UAL_LLM_KEY") or os.getenv("OPENAI_API_KEY") or "EMPTY"
        self.base_url = base_url or os.getenv("UAL_LLM_BASE_URL")
        self.model = model or os.getenv("UAL_LLM_MODEL") or "gpt-3.5-turbo"
        self.client = None
        
        # Initialize client if key is present (even 'EMPTY' for local LLMs) and library is available
        if OpenAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            logging.warning("OpenAI client not initialized. Missing key or library.")

    def generate_ual_graph(self, user_prompt: str, atlas_concepts: List[Dict]) -> Dict[str, Any]:
        """
        Generates a UAL Graph JSON (nodes/edges) from user prompt using LLM.
        """
        if not self.client:
            return self._fallback_rule_based(user_prompt, atlas_concepts)

        system_prompt = self._build_system_prompt(atlas_concepts)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logging.error(f"LLM generation failed: {e}")
            return self._fallback_rule_based(user_prompt, atlas_concepts)

    def _build_system_prompt(self, atlas_concepts: List[Dict]) -> str:
        """
        Constructs a prompt with the available UAL Atlas vocabulary.
        """
        concepts_str = "\n".join([f"- {c['name']} (ID: {c['hex']}, Category: {c['category']})" for c in atlas_concepts])
        
        return f"""You are a UAL (Universal Agent Language) Architect. 
Your goal is to convert natural language mission instructions into a JSON graph structure for the UAL Studio editor.

Available UAL Concepts (Atlas):
{concepts_str}

Output Format (JSON):
{{
  "nodes": [
    {{ "id": "node_1", "name": "concept_name", "semantic_id": 161 (int), "category": "Category" }}
  ],
  "edges": [
    {{ "source": "node_1", "target": "node_2", "relation": "next" }}
  ]
}}

Rules:
1. Only use concepts from the provided Atlas list.
2. If a concept is missing, try to map to the closest one or ignore.
3. Connect actions in a logical sequence using edges.
4. Position is not needed, the frontend will handle layout.
"""

    def _fallback_rule_based(self, text: str, atlas_concepts: List[Dict]) -> Dict[str, Any]:
        """
        Simple keyword matching fallback with basic stemming.
        """
        nodes = []
        edges = []
        # Normalize text: lower case, remove punctuation
        import re
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        prev_id = None
        
        # Build lookup map
        name_map = {c['name'].lower(): c for c in atlas_concepts}
        
        # Add aliases (Common English verbs -> UAL Actions)
        aliases = {
            # Movement
            "fly": "move", "flies": "move", "flying": "move",
            "go": "move", "goes": "move", "going": "move",
            "navigate": "move", "navigates": "move",
            "return": "move", "returns": "move", # often maps to move or specific return action
            
            # Hover
            "hover": "hover", "hovers": "hover", "hovering": "hover",
            "wait": "hover", "waits": "hover", "stop": "hover",
            "take off": "hover", # Approximation
            
            # Scan
            "scan": "scan", "scans": "scan", "scanning": "scan",
            "look": "scan", "looks": "scan", "search": "scan",
            "find": "scan",
            
            # Grab/Release
            "grab": "grab", "grabs": "grab", "take": "grab", "pick": "grab",
            "drop": "release", "drops": "release", "release": "release", "place": "release",
            
            # Common Entities
            "drone": "drone", "uav": "drone",
            "package": "package", "item": "package", "cargo": "package",
            "base": "base", "home": "base",
            "warehouse": "base" # Map warehouse to base for now
        }
        
        count = 0
        for word in words:
            # Check direct match or alias
            key = word
            if word in aliases:
                key = aliases[word]
            
            # Check singular form for nouns (basic)
            if key not in name_map and key.endswith('s'):
                if key[:-1] in name_map:
                    key = key[:-1]
            
            concept = name_map.get(key)
            if concept:
                node_id = f"gen_{count}"
                nodes.append({
                    "id": node_id,
                    "name": concept['name'],
                    "semantic_id": concept['id'],
                    "category": concept['category'],
                    "hex": concept['hex']
                })
                
                if prev_id:
                    edges.append({
                        "source": prev_id,
                        "target": node_id,
                        "relation": "next"
                    })
                
                prev_id = node_id
                count += 1
                
        return {"nodes": nodes, "edges": edges}
