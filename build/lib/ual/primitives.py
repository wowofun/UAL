from enum import IntEnum
from typing import List, Optional
from .ual_pb2 import Graph, Node, Edge, Header

class SemanticPrime(IntEnum):
    """
    递归语义元 (Recursive Semantic Primitives)
    借鉴 NSM (Natural Semantic Metalanguage) 理论。
    ID 范围：0x010 - 0x09F (保留低位 ID)
    """
    # 核心 (Substantives)
    I = 0x010      # 我
    YOU = 0x011    # 你
    SOMEONE = 0x012 # 某人
    SOMETHING = 0x013 # 某物/某事
    PEOPLE = 0x014 # 人们
    BODY = 0x015   # 身体

    # 心理谓词 (Mental Predicates)
    THINK = 0x020  # 思考
    KNOW = 0x021   # 知道
    WANT = 0x022   # 想要
    FEEL = 0x023   # 感觉
    SEE = 0x024    # 看见
    HEAR = 0x025   # 听见

    # 逻辑与量词 (Logic & Quantifiers)
    NOT = 0x030    # 不/非
    MAYBE = 0x031  # 可能
    CAN = 0x032    # 能
    BECAUSE = 0x033 # 因为
    IF = 0x034     # 如果
    VERY = 0x035   # 非常
    MORE = 0x036   # 更多

    # 动作与事件 (Actions & Events)
    DO = 0x040     # 做
    HAPPEN = 0x041 # 发生
    MOVE = 0x042   # 移动 (Move/Go)
    
    # 存在与拥有 (Existence & Possession)
    THERE_IS = 0x050 # 存在
    HAVE = 0x051     # 拥有

    # 空间与时间 (Space & Time)
    WHERE = 0x060  # 哪里
    WHEN = 0x061   # 何时
    NOW = 0x062    # 现在
    BEFORE = 0x063 # 之前
    AFTER = 0x064  # 之后

    # 评估 (Evaluators)
    GOOD = 0x070   # 好
    BAD = 0x071    # 坏
    TRUE = 0x072   # 真
    FALSE = 0x073  # 假

class PrimitiveBuilder:
    """
    语义元组合器
    用于构建 Zero-shot 概念定义。
    """
    
    @staticmethod
    def define_concept(concept_name: str, ual_core, composition: List[tuple]) -> Graph:
        """
        使用语义元定义新概念。
        composition: list of (SemanticPrime, RelationType, Target)
        Example: "Refuse" = I + WANT + NOT + DO + THIS
        """
        graph = Graph()
        root_node = ual_core.create_node(Node.ENTITY, value=concept_name, id="def_root")
        graph.nodes.append(root_node)
        
        # 简单链式构建或星型构建
        # 这里简化为：Concept IS composed of [Primes...]
        
        for i, (prime, relation) in enumerate(composition):
            p_node = ual_core.create_node(Node.ENTITY, semantic_id=prime, id=f"prime_{i}")
            graph.nodes.append(p_node)
            
            edge = ual_core.create_edge(root_node.id, p_node.id, relation)
            graph.edges.append(edge)
            
        return graph

def get_primitive_name(prime_id: int) -> Optional[str]:
    try:
        return SemanticPrime(prime_id).name
    except ValueError:
        return None
