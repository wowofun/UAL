import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ual import UAL

@pytest.fixture
def ual_agent():
    return UAL("Test_Agent")

def test_basic_encode_decode(ual_agent):
    """Test basic encoding and decoding of a simple command."""
    command = "Move to Kitchen"
    encoded = ual_agent.encode(command)
    assert isinstance(encoded, bytes)
    assert len(encoded) > 0
    
    decoded = ual_agent.decode(encoded)
    assert isinstance(decoded, dict)
    assert "Move" in decoded['natural_language'] or "move" in decoded['natural_language'].lower()

def test_parameter_extraction(ual_agent):
    """Test if parameters like 'Kitchen' are correctly extracted/preserved."""
    command = "Move to Kitchen"
    encoded = ual_agent.encode(command)
    decoded = ual_agent.decode(encoded)
    
    # Check if 'Kitchen' entity is present in nodes
    nodes = decoded.get('nodes', [])
    found_kitchen = False
    for node in nodes:
        # Check semantic ID or string value if available
        # Assuming Kitchen has a specific ID or is a known entity
        # In a real test we might check specific IDs from atlas
        pass
    
    # Simple check on NL reconstruction
    assert "Kitchen".lower() in decoded['natural_language'].lower()

def test_signature_verification(ual_agent):
    """Test that signature verification works (mocked in current impl)."""
    command = "Test Command"
    encoded = ual_agent.encode(command)
    
    # Decode should succeed
    decoded = ual_agent.decode(encoded)
    assert "error" not in decoded
