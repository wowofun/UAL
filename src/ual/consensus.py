import hashlib
import time
import random
from typing import Dict, List, Optional, Tuple
from .atlas import UniversalAtlas

class ConsensusNode:
    """
    UAL 分布式共识节点 (Decentralized Semantic Consensus Node)
    
    模拟 Gossip 协议，用于在去中心化网络中传播和验证新语义。
    当某个新语义的置信度超过阈值时，自动晋升为 Proposed Atlas 候选词。
    """
    
    def __init__(self, node_id: str, atlas: UniversalAtlas):
        self.node_id = node_id
        self.atlas = atlas
        # 候选字典: {concept_hash: {"concept": str, "id": int, "votes": int, "timestamp": float}}
        self.proposed_candidates: Dict[str, Dict] = {}
        # 已知节点列表 (模拟 P2P 网络)
        self.peers: List['ConsensusNode'] = []
        # 共识阈值
        self.CONSENSUS_THRESHOLD = 5 
        
    def add_peer(self, peer: 'ConsensusNode'):
        """添加邻居节点"""
        if peer not in self.peers:
            self.peers.append(peer)
            
    def propose_new_concept(self, concept: str, semantic_id: int):
        """
        发起新语义提案
        """
        concept_hash = self._hash_concept(concept)
        if concept_hash not in self.proposed_candidates:
            self.proposed_candidates[concept_hash] = {
                "concept": concept,
                "id": semantic_id,
                "votes": 1,  # 自己的一票
                "timestamp": time.time(),
                "proposer": self.node_id
            }
            # Gossip 传播
            self._gossip(concept_hash)
            
    def receive_proposal(self, proposal_data: Dict):
        """
        接收来自其他节点的提案 (Gossip)
        """
        concept = proposal_data["concept"]
        concept_hash = self._hash_concept(concept)
        
        # 1. 验证: 检查是否冲突 (简单模拟验证过程)
        if self.atlas.get_id(concept) is not None:
            # 已存在于标准字典，忽略
            return
            
        if concept_hash not in self.proposed_candidates:
            # 新提案，记录并投票
            self.proposed_candidates[concept_hash] = proposal_data
            self.proposed_candidates[concept_hash]["votes"] += 1
            print(f"[{self.node_id}] Verified & Voted for '{concept}' (Votes: {self.proposed_candidates[concept_hash]['votes']})")
            
            # 继续传播
            self._gossip(concept_hash)
            
            # 检查共识
            self._check_consensus(concept_hash)
        else:
            # 已知提案，增加票数 (模拟网络中多路径收到)
            self.proposed_candidates[concept_hash]["votes"] += 1
            self._check_consensus(concept_hash)

    def _gossip(self, concept_hash: str):
        """
        随机传播给部分邻居 (Gossip Protocol)
        """
        if not self.peers:
            return
            
        # 随机选择 3 个邻居传播
        targets = random.sample(self.peers, min(3, len(self.peers)))
        proposal = self.proposed_candidates[concept_hash]
        
        for peer in targets:
            peer.receive_proposal(proposal)

    def _check_consensus(self, concept_hash: str):
        """
        检查是否达成共识
        """
        candidate = self.proposed_candidates[concept_hash]
        if candidate["votes"] >= self.CONSENSUS_THRESHOLD:
            self._finalize_consensus(candidate)

    def _finalize_consensus(self, candidate: Dict):
        """
        达成共识，正式写入本地 Proposed Atlas
        """
        concept = candidate["concept"]
        sem_id = candidate["id"]
        
        # 模拟写入 Atlas 的动态区
        # 注意: 在真实区块链中，这里会生成区块
        if self.atlas.get_id(concept) is None:
            print(f"[{self.node_id}] 🎉 CONSENSUS REACHED! '{concept}' -> {hex(sem_id)} added to Proposed Atlas.")
            self.atlas.register_dynamic_concept(sem_id, concept)

    def _hash_concept(self, concept: str) -> str:
        return hashlib.sha256(concept.encode()).hexdigest()

# 简单的模拟网络管理器
class ConsensusNetwork:
    def __init__(self):
        self.nodes: List[ConsensusNode] = []
        
    def add_node(self, node: ConsensusNode):
        self.nodes.append(node)
        # 简单全连接拓扑用于演示
        for other in self.nodes:
            if other != node:
                other.add_peer(node)
                node.add_peer(other)
