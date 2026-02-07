import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ual import UAL
from ual.parser import RuleBasedParser

@pytest.fixture
def parser():
    return RuleBasedParser()

def test_if_then_logic(parser):
    """Test parsing of IF-THEN structures."""
    text = "If temperature is high then turn on fan"
    nodes, edges, meta = parser.parse(text)
    
    # Check for Logic nodes
    logic_nodes = [n for n in nodes if n.type == 4] # Node.LOGIC = 4
    assert len(logic_nodes) >= 1 # IF (and potentially THEN)
    
    # Check edges
    has_condition_edge = any(e.relation == 4 for e in edges) # CONDITION = 4
    has_consequence_edge = any(e.relation == 5 for e in edges) # CONSEQUENCE = 5
    
    assert has_condition_edge
    assert has_consequence_edge

def test_temporal_logic(parser):
    """Test parsing of WAIT/DELAY."""
    text = "Wait 10 minutes"
    nodes, edges, meta = parser.parse(text)
    
    # Check for value node '10' and temporal concept
    value_nodes = [n for n in nodes if n.type == 6] # Node.VALUE = 6
    assert len(value_nodes) > 0
    assert value_nodes[0].str_val == "10"

def test_unknown_concept_fallback(parser):
    """Test handling of unknown concepts (Negative Case)."""
    text = "Activate the FluxCapacitor"
    nodes, edges, meta = parser.parse(text)
    
    # 'FluxCapacitor' should likely be treated as an UNKNOWN node or generic entity
    # depending on parser robustness.
    # In v0.2.1, it might just be skipped or added as raw text node if not found in atlas.
    
    # We assert that it doesn't crash
    assert len(nodes) > 0

def test_invalid_input(parser):
    """Test handling of empty or nonsense input."""
    text = ""
    nodes, edges, meta = parser.parse(text)
    assert len(nodes) == 0
    
    text = "   "
    nodes, edges, meta = parser.parse(text)
    assert len(nodes) == 0
