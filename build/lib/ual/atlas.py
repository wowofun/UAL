from typing import Dict, Optional, Tuple

import os
import yaml

class UniversalAtlas:
    """
    UAL 语义映射表 (Universal Atlas)
    管理语义 ID 到自然语言概念的映射。
    """
    
    def __init__(self):
        # 基础词汇表 (MVP 示例)
        self._id_to_concept: Dict[int, str] = {
            # 动作 (Actions) - 0x0A0 range
            0x0A1: "move",       # 移动 (return, go, navigate)
            0x0A2: "scan",       # 扫描 (search, look)
            0x0A3: "grab",       # 抓取 (take, pick, lift)
            0x0A4: "release",    # 释放 (drop, place)
            0x0A5: "hover",      # 悬停 (stop, wait, hold)
            
            # 实体 (Entities) - 0x0E0 range
            0x0E1: "drone",      # 无人机
            0x0E2: "target",     # 目标 (area, zone)
            0x0E3: "obstacle",   # 障碍物
            0x0E4: "base",       # 基地 (home, charger)
            0x0E5: "package",    # 包裹 (item, cargo)
            0x0E6: "kitchen",    # 厨房
            0x0E7: "shelf",      # 货架
            
            # 属性 (Properties) - 0x0B0 range
            0x0B1: "speed",      # 速度
            0x0B2: "position",   # 位置
            0x0B3: "status",     # 状态
            0x0B4: "battery",    # 电量
            
            # 逻辑 (Logic) - 0x0C0 range
            0x0C1: "if",
            0x0C2: "then",
            0x0C3: "else",
            0x0C4: "and",
            0x0C5: "or",
            0x0C6: "not",        # Explicit NOT
            
            # 模态 (Modal) - 0x0D0 range
            0x0D1: "must",
            0x0D2: "should",
            0x0D3: "can",

            # 元认知 (Meta-Cognition) - 0x0F0 range
            0x0F1: "uncertainty", # 不确定性
            0x0F2: "probability", # 概率
            0x0F3: "confidence",  # 置信度
            0x0F4: "belief",      # 信念
        }
        
        # 反向映射
        self._concept_to_id: Dict[str, int] = {v: k for k, v in self._id_to_concept.items()}
        
        # 别名表 (Aliases)
        self._aliases: Dict[str, int] = {
            "return": 0x0A1,
            "go": 0x0A1,
            "navigate": 0x0A1,
            "search": 0x0A2,
            "look": 0x0A2,
            "take": 0x0A3,
            "pick": 0x0A3,
            "drop": 0x0A4,
            "place": 0x0A4,
            "stop": 0x0A5,
            "wait": 0x0A5,
            "home": 0x0E4,
            "area": 0x0E2,
            "zone": 0x0E2,
            "item": 0x0E5,
            "cargo": 0x0E5
        }
        
        # 动态扩展部分
        self._dynamic_registry: Dict[int, str] = {}
        self._dynamic_concept_to_id: Dict[str, int] = {} # 修复动态注册的反向映射
        
        # 命名空间 (Namespaces)
        self._namespaces: Dict[str, Dict[int, str]] = {
            "warehouse_v1": {
                0x1001: "pallet",
                0x1002: "forklift"
            },
            "medical_v1": {
                0x2001: "scalpel",
                0x2002: "suture",
                0x2003: "monitor"
            }
        }
        self._active_namespaces: set[str] = set()

        # Load external Atlas if exists
        self.load_from_yaml(os.path.join(os.path.dirname(__file__), "atlas.yaml"))
        
        # Load packages from src/ual/packages/
        packages_dir = os.path.join(os.path.dirname(__file__), "packages")
        if os.path.exists(packages_dir):
            for filename in os.listdir(packages_dir):
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    self.load_from_yaml(os.path.join(packages_dir, filename))

    def load_from_yaml(self, path: str):
        """Load atlas definitions from a YAML file."""
        if not os.path.exists(path):
            return
            
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
            if "concepts" in data:
                for sid_str, names in data["concepts"].items():
                    # Handle hex string parsing (e.g. "0x0A1" -> 161)
                    if isinstance(sid_str, int):
                        sid = sid_str
                    else:
                        sid_str_clean = str(sid_str).strip()
                        if sid_str_clean.lower().startswith('0x'):
                            sid = int(sid_str_clean, 16)
                        else:
                            sid = int(sid_str_clean)

                    if not names: continue
                    
                    # First name is the primary concept
                    primary = names[0]
                    self._id_to_concept[sid] = primary
                    self._concept_to_id[primary] = sid
                    
                    # Rest are aliases
                    for alias in names[1:]:
                        self._aliases[alias] = sid
                        
            print(f"✅ Loaded Atlas from {path}")
        except Exception as e:
            print(f"⚠️ Failed to load atlas yaml: {e}")

    def register_dynamic_concept(self, id: int, concept: str):
        """
        运行时注册新概念 (用户扩展区)
        """
        concept = concept.lower()
        self._dynamic_registry[id] = concept
        self._dynamic_concept_to_id[concept] = id # Fix: Update reverse mapping

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
        
        # 0. Plural Handling (Improved)
        sid = self._lookup_id(concept)
        if sid: return sid
        
        # Try singular forms
        singulars = []
        if concept.endswith('ies'):
            singulars.append(concept[:-3] + 'y')
        elif concept.endswith('es'):
            singulars.append(concept[:-2])
            singulars.append(concept[:-1])
        elif concept.endswith('s') and not concept.endswith('ss'):
            singulars.append(concept[:-1])
            
        for s in singulars:
            sid = self._lookup_id(s)
            if sid: return sid

        return None
        
    def _lookup_id(self, concept: str) -> Optional[int]:
        # 1. 查基础表
        if concept in self._concept_to_id:
            return self._concept_to_id[concept]
            
        # 1.5 查别名
        if concept in self._aliases:
            return self._aliases[concept]

        # 1.8 查动态表 (New)
        if concept in self._dynamic_concept_to_id:
            return self._dynamic_concept_to_id[concept]
            
        # 2. 查活跃命名空间 (低效遍历，MVP 适用)
        for ns in self._active_namespaces:
            if ns in self._namespaces:
                # 优化：应该先构建反向索引，这里暂时遍历
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
