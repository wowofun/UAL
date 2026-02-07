import time
import uuid
import hashlib
from typing import Dict, List, Optional, Union, Any
from . import ual_pb2
from .atlas import get_atlas
from .utils import generate_message_id, compute_semantic_hash, sign_message, verify_signature
from .state import StateTracker
from .parser import SemanticParser, RuleBasedParser, LLMParser
from .consensus import ConsensusNode

class UAL:
    """
    UAL Core API
    """
    
    def __init__(self, agent_id: str, private_key: str = "default_key", llm_model_path: str = None):
        self.agent_id = agent_id
        self.private_key = private_key
        self.atlas = get_atlas()
        self.tracker = StateTracker()
        
        # Initialize Semantic Parser (LLM or Rule-Based)
        if llm_model_path:
            self.parser = LLMParser(llm_model_path)
        else:
            self.parser = RuleBasedParser()
            
        # Initialize Consensus Node
        self.consensus_node = ConsensusNode(agent_id, self.atlas)

    def create_node(self, node_type, semantic_id: int = 0, id: str = None, value: Any = None) -> ual_pb2.Node:
        """
        创建一个节点
        """
        node = ual_pb2.Node()
        node.id = id if id else str(uuid.uuid4())[:8]
        node.type = node_type
        if semantic_id:
            node.semantic_id = semantic_id
            
        if value is not None:
            if isinstance(value, str):
                node.str_val = value
            elif isinstance(value, (int, float)):
                node.num_val = float(value)
            elif isinstance(value, bool):
                node.bool_val = value
            elif isinstance(value, bytes):
                node.blob_val = value
                
        return node

    def create_edge(self, source_id: str, target_id: str, relation_type, weight: float = 1.0) -> ual_pb2.Edge:
        """
        创建一个边
        """
        edge = ual_pb2.Edge()
        edge.source_id = source_id
        edge.target_id = target_id
        edge.relation = relation_type
        edge.weight = weight
        return edge

    def create_graph(self, nodes: List[ual_pb2.Node], edges: List[ual_pb2.Edge], context_id: str = "") -> ual_pb2.Graph:
        """
        创建一个图
        """
        graph = ual_pb2.Graph()
        graph.nodes.extend(nodes)
        graph.edges.extend(edges)
        graph.context_id = context_id
        return graph

    def create_env_frame(self, frame_id: str = "world", origin: List[float] = None, orientation: List[float] = None, unit: str = "meter", timestamp: float = None) -> Dict[str, Any]:
        """
        Create an Environmental Frame dictionary for metadata.
        """
        return {
            "frame_id": frame_id,
            "origin": origin if origin else [0.0, 0.0, 0.0],
            "orientation": orientation if orientation else [0.0, 0.0, 0.0, 1.0],
            "unit": unit,
            "timestamp": timestamp if timestamp else time.time()
        }

    def parse(self, natural_language: str):
        """
        Explicit parse method returning nodes, edges, metadata.
        """
        return self.parser.parse(natural_language)

    def encode_from_graph(self, 
                          nodes: List[ual_pb2.Node], 
                          edges: List[ual_pb2.Edge], 
                          metadata: Dict[str, Any],
                          receiver_id: str = "broadcast",
                          context_id: str = "",
                          use_delta: bool = False) -> bytes:
        """
        Encode from pre-parsed graph structure.
        """
        # 2. Construct Graph
        graph = self.create_graph(nodes, edges, context_id)
        
        # 3. State Tracking & Delta Compression
        full_graph = graph
        final_graph = full_graph
        is_delta_msg = False
        parent_hash = ""
        
        if use_delta and receiver_id != "broadcast":
            # Check if we can send a delta
            # Logic: Compute full hash, compare with peer's known state
            delta_graph = self.tracker.compute_delta(full_graph, receiver_id)
            if delta_graph != full_graph: # Simplified check
                final_graph = delta_graph
                is_delta_msg = True
                parent_hash = self.tracker.last_hashes.get(receiver_id, "")
        
        # 4. Construct Message
        msg = ual_pb2.UALMessage()
        
        # Header
        msg.header.sender_id = self.agent_id
        msg.header.receiver_id = receiver_id
        msg.header.timestamp = int(time.time())
        msg.header.message_id = generate_message_id(self.agent_id)
        msg.header.protocol_version = "0.2.0"
        msg.header.is_delta = is_delta_msg
        msg.header.parent_hash = parent_hash
        
        # Apply Metadata from Parser (Urgency, Style, EnvFrame)
        msg.header.urgency = metadata.get("urgency", 0.0)
        msg.header.style = int(metadata.get("style", 0))
        
        if "env_frame" in metadata:
            ef_data = metadata["env_frame"]
            ef = msg.header.env_frame
            ef.frame_id = str(ef_data.get("frame_id", "world"))
            if "origin" in ef_data:
                ef.origin.extend(ef_data["origin"])
            if "orientation" in ef_data:
                ef.orientation.extend(ef_data["orientation"])
            ef.unit = str(ef_data.get("unit", "meter"))
            ef.timestamp = float(ef_data.get("timestamp", time.time()))
        
        # Content
        msg.content.CopyFrom(final_graph)
        
        # Semantic Hash
        msg.header.semantic_hash = compute_semantic_hash(msg.content.SerializeToString(deterministic=True))
        
        # Signature
        payload_bytes = msg.content.SerializeToString(deterministic=True)
        sign_payload = msg.header.SerializeToString(deterministic=True) + payload_bytes
        msg.signature.sign_data = sign_message(sign_payload, self.private_key)
        msg.signature.algorithm = "sha256_hmac_mock"
        
        return msg.SerializeToString()

    def encode(self, 
               natural_language: str, 
               receiver_id: str = "broadcast",
               context_id: str = "",
               embedding_map: Dict[str, List[float]] = None,
               use_delta: bool = False) -> bytes:
        """
        将自然语言转换为 UAL 二进制格式 (Protobuf)
        
        Args:
            natural_language: 自然语言指令
            receiver_id: 接收者 ID
            context_id: 上下文 ID
            embedding_map: 词汇到向量的映射 {"obstacle": [0.1, 0.2...]}
            use_delta: 是否启用增量压缩
        """
        # 1. Parse Natural Language -> Semantic Graph
        nodes, edges, metadata = self.parser.parse(natural_language)
        
        # Inject Embeddings if provided
        # (Naive injection: if a node's concept matches a key in embedding_map, inject)
        if embedding_map:
            # Re-map semantic IDs to concepts to check against embedding_map
            # This is inefficient but functional for MVP
            for node in nodes:
                concept = self.atlas.get_concept(node.semantic_id)
                if concept and concept in embedding_map:
                    vec = ual_pb2.Vector()
                    vec.values.extend(embedding_map[concept])
                    vec.model_name = "clip-mock"
                    node.embedding.CopyFrom(vec)
        
        return self.encode_from_graph(nodes, edges, metadata, receiver_id, context_id, use_delta)

    def decode(self, ual_binary: bytes) -> Dict[str, Any]:
        """
        将 UAL 二进制解码为结构化数据/自然语言描述
        """
        msg = ual_pb2.UALMessage()
        msg.ParseFromString(ual_binary)
        
        # 验证 (可选)
        if not self.validate(msg):
            return {"error": "Invalid signature"}
        
        base_info = {
            "sender": msg.header.sender_id,
            "timestamp": msg.header.timestamp,
            "semantic_hash": msg.header.semantic_hash,
            "is_delta": msg.header.is_delta
        }
            
        # 检查 Payload 类型
        if msg.HasField("handshake"):
             handshake = msg.handshake
             # 自动加载 Namespaces (如果提供)
             if handshake.namespaces:
                 for ns in handshake.namespaces:
                     self.atlas.load_namespace(ns)
                     
             return {
                 **base_info,
                 "type": "handshake",
                 "agent_id": handshake.agent_id,
                 "capabilities": list(handshake.capabilities),
                 "namespaces": list(handshake.namespaces),
                 "compute_power": handshake.compute_power,
                 "natural_language": f"Handshake from {handshake.agent_id} (Compute: {handshake.compute_power}, NS: {handshake.namespaces})"
             }
        
        if msg.HasField("content"):
            graph = msg.content
            
            # Delta 还原
            if msg.header.is_delta:
                # 尝试从 Tracker 还原
                graph = self.tracker.apply_delta(graph, msg.header.sender_id)
            
            # 解析 Graph
            description = []
            
            node_map = {n.id: n for n in graph.nodes}
            adj = {n.id: [] for n in graph.nodes}
            for edge in graph.edges:
                if edge.source_id in adj:
                    adj[edge.source_id].append(edge.target_id)
                
            actions = [n for n in graph.nodes if 0xA0 <= n.semantic_id < 0xB0] # Improved Action Check
            
            nl_parts = []
            
            if not actions:
                 # If no actions, list all other nodes
                 other_nodes = [n for n in graph.nodes if not (0xA0 <= n.semantic_id < 0xB0)]
                 parts = []
                 for n in other_nodes:
                     if n.type == ual_pb2.Node.VALUE and n.HasField("str_val"):
                         parts.append(n.str_val)
                     elif n.semantic_id:
                         c = self.atlas.get_concept(n.semantic_id)
                         if c: parts.append(c)
                 if parts:
                     nl_parts.append(" ".join(parts))
            
            for action in actions:
                action_concept = self.atlas.get_concept(action.semantic_id) or "Unknown_Action"
                
                target_concepts = []
                if action.id in adj:
                    for target_id in adj[action.id]:
                        if target_id in node_map:
                            target_node = node_map[target_id]
                            concept = self.atlas.get_concept(target_node.semantic_id)
                            
                            # 检查 Embedding
                            extra = ""
                            if target_node.HasField("embedding"):
                                extra = " [Vision]"
                                
                            if concept:
                                target_concepts.append(concept + extra)
                            elif target_node.type == ual_pb2.Node.VALUE:
                                target_concepts.append(target_node.str_val + extra)
                
                phrase = f"{action_concept} " + " ".join(target_concepts)
                nl_parts.append(phrase)
                
            return {
                **base_info,
                "type": "graph",
                "natural_language": "; ".join(nl_parts),
                "raw_graph": str(msg.content), # Debug info
            }
        
        return {"error": "Unknown payload type"}

    def validate(self, msg: ual_pb2.UALMessage) -> bool:
        """验证消息完整性和签名"""
        if msg.HasField("content"):
             payload_bytes = msg.content.SerializeToString(deterministic=True)
        elif msg.HasField("handshake"):
             payload_bytes = msg.handshake.SerializeToString(deterministic=True)
        else:
             payload_bytes = b""
             
        payload = msg.header.SerializeToString(deterministic=True) + payload_bytes
        
        # 这里假设我们知道发送者的公钥，MVP 中简单使用 dummy_key
        is_valid = verify_signature(payload, msg.signature.sign_data, "dummy_key")
        return True # MVP: Bypass strict check

    def create_handshake(self, 
                         capabilities: List[str] = None, 
                         compute_power: int = 100,
                         namespaces: List[str] = None) -> bytes:
        """创建握手消息"""
        if capabilities is None:
            capabilities = ["ual_v2", "image_processing"]
        if namespaces is None:
            namespaces = []
            
        handshake = ual_pb2.Handshake()
        handshake.agent_id = self.agent_id
        handshake.capabilities.extend(capabilities)
        handshake.namespaces.extend(namespaces)
        handshake.public_key = "mock_public_key"
        handshake.compute_power = compute_power
        
        msg = ual_pb2.UALMessage()
        
        # Header
        msg.header.sender_id = self.agent_id
        msg.header.receiver_id = "broadcast"
        msg.header.timestamp = int(time.time())
        msg.header.message_id = generate_message_id(self.agent_id)
        msg.header.protocol_version = "0.2.0"
        
        msg.handshake.CopyFrom(handshake)
        
        # Signature
        payload_bytes = handshake.SerializeToString(deterministic=True)
        sign_payload = msg.header.SerializeToString(deterministic=True) + payload_bytes
        msg.signature.sign_data = sign_message(sign_payload, self.private_key)
        msg.signature.algorithm = "sha256_hmac_mock"
        
        return msg.SerializeToString()
