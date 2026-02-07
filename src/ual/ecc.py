import numpy as np
from typing import List, Optional, Any
import logging
from . import ual_pb2

logger = logging.getLogger(__name__)

class ErrorCorrection:
    """
    语义纠错与平滑衰减 (Error Correction & Graceful Degradation)
    """

    @staticmethod
    def compute_parity(data: bytes) -> int:
        """Compute simple XOR parity byte"""
        parity = 0
        for byte in data:
            parity ^= byte
        return parity

    @staticmethod
    def add_redundancy(data: bytes) -> bytes:
        """
        Add 1 byte of XOR parity for simple error detection/correction simulation.
        Real world: Reed-Solomon.
        """
        parity = ErrorCorrection.compute_parity(data)
        return data + bytes([parity])

    @staticmethod
    def verify_and_repair_bitstream(data_with_parity: bytes) -> Optional[bytes]:
        """
        Verify parity. If failed, attempt single-bit flip repair (Brute Force).
        """
        if len(data_with_parity) < 1:
            return None
            
        data = data_with_parity[:-1]
        received_parity = data_with_parity[-1]
        
        # 1. Check if clean
        if ErrorCorrection.compute_parity(data) == received_parity:
            return data
            
        logger.warning("Parity check failed. Attempting bit-flip repair...")
        
        # 2. Attempt single-byte repair (Simulate "Bit Flip")
        # In a real Reed-Solomon, we would solve equations.
        # Here we just try flipping bits in each byte and see if parity matches.
        # This is expensive O(N) but fine for small UAL packets.
        data_array = bytearray(data)
        for i in range(len(data_array)):
            original_byte = data_array[i]
            # Try all 8 bits
            for bit in range(8):
                data_array[i] = original_byte ^ (1 << bit)
                if ErrorCorrection.compute_parity(data_array) == received_parity:
                    logger.info(f"Repaired bit error at byte {i}, bit {bit}")
                    return bytes(data_array)
            data_array[i] = original_byte # Restore
            
        logger.error("Bitstream repair failed.")
        return None

    @staticmethod
    def semantic_repair(graph_nodes: List[ual_pb2.Node], atlas: Any, context_cache: List[str] = None):
        """
        基于上下文的概率补全。
        如果节点 ID 丢失但有 Embedding，或反之。
        或者根据 Context Cache 猜测意图。
        """
        repaired_count = 0
        for node in graph_nodes:
            # Case 1: Semantic ID missing (0) but has context hint or is Action
            if node.semantic_id == 0:
                if node.type == ual_pb2.Node.ACTION:
                    # Try to guess from context cache
                    if context_cache and "flight" in context_cache:
                         node.semantic_id = 0x0A1 # Assume 'move'
                         node.str_val = "move (repaired)"
                         repaired_count += 1
                         logger.info(f"Repaired Action Node {node.id} -> move (based on 'flight' context)")
                    elif node.HasField("embedding"):
                        # Mock embedding lookup
                        node.semantic_id = 0x0A1
                        repaired_count += 1
                        logger.info(f"Repaired Node {node.id} using embedding")

            # Case 2: Broken parameter values (e.g. outlier detection)
            if node.type == ual_pb2.Node.VALUE and node.HasField("num_val"):
                 # If we expect a percentage but get > 100 or < 0
                 if node.num_val > 1000000: # Clearly garbage
                     node.num_val = 0
                     logger.warning(f"Clamped garbage value in Node {node.id}")
                     repaired_count += 1

        return repaired_count

