import hashlib
from typing import Dict, Any, List, Optional, Set
from . import ual_pb2

class StateTracker:
    """
    UAL 状态追踪器 (State Tracker)
    用于管理会话状态，支持增量压缩 (Delta Compression)。
    """
    
    def __init__(self):
        # sender_id -> {node_id: NodeObject}
        # 接收端缓存：用于还原 Delta
        self.peer_full_nodes: Dict[str, Dict[str, ual_pb2.Node]] = {}
        
        # receiver_id -> {node_id: node_hash}
        # 发送端缓存：用于计算 Delta
        self.sent_states: Dict[str, Dict[str, str]] = {}
        
        # 记录上一帧的 Semantic Hash
        self.last_hashes: Dict[str, str] = {}

    def get_node_hash(self, node: ual_pb2.Node) -> str:
        """计算单个节点的哈希"""
        return hashlib.sha256(node.SerializeToString(deterministic=True)).hexdigest()

    def compute_delta(self, full_graph: ual_pb2.Graph, receiver_id: str) -> ual_pb2.Graph:
        """
        计算相对于发送给 receiver_id 的上一帧的 Delta。
        """
        if receiver_id not in self.sent_states:
            self.sent_states[receiver_id] = {}
            self.last_hashes[receiver_id] = ""
            
        prev_state = self.sent_states[receiver_id]
        new_state = {}
        
        delta_graph = ual_pb2.Graph()
        delta_graph.context_id = full_graph.context_id
        
        # 1. 处理节点
        current_node_ids = set()
        for node in full_graph.nodes:
            node_hash = self.get_node_hash(node)
            new_state[node.id] = node_hash
            current_node_ids.add(node.id)
            
            # 增量条件：新节点 或 哈希变化
            if node.id not in prev_state or prev_state[node.id] != node_hash:
                delta_graph.nodes.append(node)
        
        # 2. 处理移除的节点
        for old_id in prev_state:
            if old_id not in current_node_ids:
                delta_graph.removed_node_ids.append(old_id)
                
        # 3. 边 (MVP: 总是全量发送边，因为边很小且逻辑复杂)
        delta_graph.edges.extend(full_graph.edges)
        
        # 更新发送状态
        self.sent_states[receiver_id] = new_state
        
        return delta_graph

    def apply_delta(self, delta_graph: ual_pb2.Graph, sender_id: str) -> ual_pb2.Graph:
        """
        将来自 sender_id 的 Delta 应用到上一帧状态，还原完整 Graph。
        """
        if sender_id not in self.peer_full_nodes:
            self.peer_full_nodes[sender_id] = {}
            
        current_nodes = self.peer_full_nodes[sender_id]
        
        # 1. 应用移除
        for rm_id in delta_graph.removed_node_ids:
            if rm_id in current_nodes:
                del current_nodes[rm_id]
                
        # 2. 应用新增/修改
        for node in delta_graph.nodes:
            current_nodes[node.id] = node
            
        # 3. 重建完整 Graph
        full_graph = ual_pb2.Graph()
        full_graph.context_id = delta_graph.context_id
        full_graph.nodes.extend(current_nodes.values())
        full_graph.edges.extend(delta_graph.edges) # 边是全量的
        
        return full_graph
