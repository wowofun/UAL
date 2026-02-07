from typing import Any, Dict, Optional
from .core import UAL

class UALBridge:
    """
    UAL Cross-LLM Plugin (跨语言桥接器)
    
    允许 LangChain / LlamaIndex 等框架直接调用 UAL 进行通信。
    模拟了 "Function Calling" 或 "Tool" 的接口。
    """
    
    def __init__(self, agent_id: str = "LLM_Bridge_Bot"):
        self.ual = UAL(agent_id)
        
    def speak(self, message: str, protocol: str = 'UAL') -> Dict[str, Any]:
        """
        High-level API for LLMs to speak UAL.
        
        Usage:
            response = bridge.speak("Drone return to base", protocol='UAL')
        """
        if protocol.upper() != 'UAL':
            return {"error": f"Unsupported protocol: {protocol}"}
            
        # 1. Encoding (LLM Thought -> UAL Binary)
        try:
            binary_payload = self.ual.encode(message)
            hex_payload = binary_payload.hex()
            
            # 2. Decoding (Simulation of loopback/verification)
            decoded = self.ual.decode(binary_payload)
            
            return {
                "status": "success",
                "original_message": message,
                "ual_binary_hex": hex_payload,
                "payload_size_bytes": len(binary_payload),
                "semantic_verification": decoded['natural_language'],
                "note": "Message successfully encoded to UAL protocol."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def as_langchain_tool(self):
        """
        Returns a dictionary compatible with LangChain tool definition.
        """
        return {
            "name": "speak_ual",
            "description": "Encodes a natural language message into UAL (Universal Agent Language) binary protocol for efficient machine-to-machine communication.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The command or information to send."
                    }
                },
                "required": ["message"]
            }
        }
