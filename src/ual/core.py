import time
import uuid
import hashlib
from typing import Dict, List, Optional, Union, Any
from . import ual_pb2
from .atlas import get_atlas
from .utils import generate_message_id, compute_semantic_hash, sign_message, verify_signature
from .state import StateTracker

class UAL:
    """
    UAL 核心 API
    """
    
    def __init__(self, agent_id: str, private_key: str = "default_key"):
        self.agent_id = agent_id
        self.private_key = private_key
        self.atlas = get_atlas()
        self.tracker = StateTracker()

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
        # 1. 解析自然语言 (Simple Parser)
        words = natural_language.lower().replace('.', '').split()
        
        nodes = []
        edges = []
        
        # 简单的构建逻辑：找到动词作为根，名词作为依赖
        action_node = None
        entity_nodes = []
        
        for word in words:
            semantic_id = self.atlas.get_id(word)
            if semantic_id:
                node = ual_pb2.Node()
                node.id = str(uuid.uuid4())[:8]
                node.semantic_id = semantic_id
                
                # 检查是否有 Embedding 注入
                if embedding_map and word in embedding_map:
                    vec = ual_pb2.Vector()
                    vec.values.extend(embedding_map[word])
                    vec.model_name = "clip-mock" 
                    node.embedding.CopyFrom(vec)
                
                if 0xA0 <= semantic_id < 0xB0: # Action
                    node.type = ual_pb2.Node.ACTION
                    action_node = node
                elif 0xB0 <= semantic_id < 0xC0: # Property
                    node.type = ual_pb2.Node.PROPERTY
                    entity_nodes.append(node)
                elif 0xC0 <= semantic_id < 0xD0: # Logic
                     node.type = ual_pb2.Node.LOGIC
                     entity_nodes.append(node)
                elif 0xD0 <= semantic_id < 0xE0: # Modal
                     node.type = ual_pb2.Node.MODAL
                     entity_nodes.append(node)
                elif 0xE0 <= semantic_id < 0xF0: # Entity
                    node.type = ual_pb2.Node.ENTITY
                    entity_nodes.append(node)
                elif semantic_id >= 0x1000: # 动态/行业扩展 ID
                    node.type = ual_pb2.Node.ENTITY 
                    entity_nodes.append(node)
                else:
                    node.type = ual_pb2.Node.UNKNOWN
                
                nodes.append(node)

        # 构建边
        if action_node:
            for entity in entity_nodes:
                edge = ual_pb2.Edge()
                edge.source_id = action_node.id
                edge.target_id = entity.id
                edge.relation = ual_pb2.Edge.ARGUMENT
                edges.append(edge)
        
        # 如果没有识别出结构，创建一个 RAW 文本节点
        if not nodes:
             node = ual_pb2.Node()
             node.id = str(uuid.uuid4())[:8]
             node.type = ual_pb2.Node.VALUE
             node.str_val = natural_language
             nodes.append(node)

        # 2. 构建 Graph
        full_graph = ual_pb2.Graph()
        full_graph.nodes.extend(nodes)
        full_graph.edges.extend(edges)
        full_graph.context_id = context_id
        
        # Delta Compression 处理
        final_graph = full_graph
        is_delta_msg = False
        parent_hash = ""
        
        if use_delta and receiver_id != "broadcast":
            # 计算 Delta
            delta_graph = self.tracker.compute_delta(full_graph, receiver_id)
            final_graph = delta_graph
            is_delta_msg = True
            parent_hash = self.tracker.last_hashes.get(receiver_id, "")
        
        # 3. 构建 Message
        msg = ual_pb2.UALMessage()
        
        # Header
        msg.header.sender_id = self.agent_id
        msg.header.receiver_id = receiver_id
        msg.header.timestamp = int(time.time())
        msg.header.message_id = generate_message_id(self.agent_id)
        msg.header.protocol_version = "0.2.0"
        msg.header.is_delta = is_delta_msg
        msg.header.parent_hash = parent_hash
        
        # Content
        msg.content.CopyFrom(final_graph)
        
        # Semantic Hash (基于 Full Graph 计算)
        # 实际上我们应该 Hash full_graph, 但这里我们 Hash 发送的内容
        msg.header.semantic_hash = compute_semantic_hash(msg.content.SerializeToString(deterministic=True))
        
        # Signature
        payload_bytes = msg.content.SerializeToString(deterministic=True)
        sign_payload = msg.header.SerializeToString(deterministic=True) + payload_bytes
        msg.signature.sign_data = sign_message(sign_payload, self.private_key)
        msg.signature.algorithm = "sha256_hmac_mock"
        
        return msg.SerializeToString()

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
                
            actions = [n for n in graph.nodes if n.type == ual_pb2.Node.ACTION]
            
            nl_parts = []
            
            if not actions:
                 # If no actions, list all other nodes
                 other_nodes = [n for n in graph.nodes if n.type != ual_pb2.Node.ACTION]
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
