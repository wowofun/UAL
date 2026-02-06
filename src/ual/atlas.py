from typing import Dict, Optional, Tuple

class UniversalAtlas:
    """
    UAL 语义映射表 (Universal Atlas)
    管理语义 ID 到自然语言概念的映射。
    """
    
    def __init__(self):
        # 基础词汇表 (MVP 示例)
        self._id_to_concept: Dict[int, str] = {
            # 动作 (Actions) - 0x0A0 range
            0x0A1: "move",       # 移动
            0x0A2: "scan",       # 扫描
            0x0A3: "grab",       # 抓取
            0x0A4: "release",    # 释放
            0x0A5: "hover",      # 悬停
            
            # 实体 (Entities) - 0x0E0 range
            0x0E1: "drone",      # 无人机
            0x0E2: "target",     # 目标
            0x0E3: "obstacle",   # 障碍物
            0x0E4: "base",       # 基地
            0x0E5: "package",    # 包裹
            
            # 属性 (Properties) - 0x0B0 range (B for attributes/properties)
            0x0B1: "speed",      # 速度
            0x0B2: "position",   # 位置
            0x0B3: "status",     # 状态
            0x0B4: "battery",    # 电量
            
            # 逻辑 (Logic) - 0x0C0 range (C for condition/logic)
            0x0C1: "if",
            0x0C2: "then",
            0x0C3: "else",
            0x0C4: "and",
            0x0C5: "or",
            
            # 模态 (Modal) - 0x0D0 range (D for duty/modal)
            0x0D1: "must",
            0x0D2: "should",
            0x0D3: "can",
        }
        
        # 反向映射
        self._concept_to_id: Dict[str, int] = {v: k for k, v in self._id_to_concept.items()}
        
        # 动态扩展部分
        self._dynamic_registry: Dict[int, str] = {}
        
        # 命名空间 (Namespaces)
        self._namespaces: Dict[str, Dict[int, str]] = {
            "warehouse_v1": {
                0x1001: "shelf", 
                0x1002: "pallet",
                0x1003: "forklift"
            },
            "medical_v1": {
                0x2001: "scalpel",
                0x2002: "suture",
                0x2003: "monitor"
            }
        }
        self._active_namespaces: set[str] = set()

    def get_concept(self, semantic_id: int) -> Optional[str]:
        """根据 ID 获取概念"""
        # 1. 查基础表
        if semantic_id in self._id_to_concept:
            return self._id_to_concept[semantic_id]
        
        # 2. 查动态表
        if semantic_id in self._dynamic_registry:
            return self._dynamic_registry[semantic_id]
            
        # 3. 查活跃命名空间
        for ns in self._active_namespaces:
            if ns in self._namespaces and semantic_id in self._namespaces[ns]:
                return self._namespaces[ns][semantic_id]
                
        return None

    def get_id(self, concept: str) -> Optional[int]:
        """根据概念获取 ID"""
        # 简单处理：转小写
        concept = concept.lower()
        
        # 1. 查基础表
        if concept in self._concept_to_id:
            return self._concept_to_id[concept]
            
        # 2. 查活跃命名空间 (低效遍历，MVP 适用)
        for ns in self._active_namespaces:
            if ns in self._namespaces:
                for sid, name in self._namespaces[ns].items():
                    if name == concept:
                        return sid
                        
        return None

    def load_namespace(self, name: str):
        """激活命名空间"""
        if name in self._namespaces:
            self._active_namespaces.add(name)
            
    def unload_namespace(self, name: str):
        """卸载命名空间"""
        if name in self._active_namespaces:
            self._active_namespaces.remove(name)

    def register_concept(self, concept: str, semantic_id: int):
        """动态注册新概念"""
        concept = concept.lower()
        self._dynamic_registry[semantic_id] = concept
        # 注意：这里没有更新反向映射，实际应用中需要处理冲突
        
    def dump_atlas(self):
        """导出当前映射表"""
        return {**self._id_to_concept, **self._dynamic_registry}

# 单例实例
_ATLAS = UniversalAtlas()

def get_atlas() -> UniversalAtlas:
    return _ATLAS
