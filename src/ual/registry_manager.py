import json
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegistryManager:
    """
    UAL 标准注册表 (Global Registry)
    管理 Global Standard IDs 和 Private IDs，避免冲突。
    模拟 IANA 机制。
    """
    
    STANDARD_RANGE = (0x0000, 0x0FFF) # 0-4095: 保留给标准定义
    INDUSTRY_RANGE = (0x1000, 0xEFFF) # 4096-61439: 行业扩展 (需注册)
    PRIVATE_RANGE  = (0xF000, 0xFFFF) # 61440+: 私有/动态扩展 (无需注册)

    def __init__(self, registry_file: str = "ual_registry.json"):
        self.registry_file = registry_file
        self.global_registry: Dict[str, int] = {} # concept -> id
        self.reverse_registry: Dict[int, str] = {} # id -> concept
        self._load_registry()

    def _load_registry(self):
        """加载本地注册表缓存"""
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                self.global_registry = data.get("concepts", {})
                self.reverse_registry = {int(k): v for k, v in data.get("ids", {}).items()}
        except FileNotFoundError:
            logger.info("No local registry found. Initializing empty registry.")
            self._init_defaults()

    def _init_defaults(self):
        """初始化默认标准词汇 (Base Atlas)"""
        # 这里仅作示例，实际应从 Atlas 导入或云端同步
        defaults = {
            "move": 0x0A1, "scan": 0x0A2, "grab": 0x0A3,
            "drone": 0x0E1, "target": 0x0E2,
            "must": 0x0D1, "if": 0x0C1
        }
        for k, v in defaults.items():
            self.register_standard_concept(k, v)

    def save_registry(self):
        """保存注册表到本地"""
        data = {
            "concepts": self.global_registry,
            "ids": self.reverse_registry
        }
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)

    def register_standard_concept(self, concept: str, id: int) -> bool:
        """注册标准概念 (IANA style)"""
        if not (self.STANDARD_RANGE[0] <= id <= self.STANDARD_RANGE[1]):
            logger.warning(f"ID {hex(id)} out of Standard Range.")
            return False
        
        if id in self.reverse_registry and self.reverse_registry[id] != concept:
             logger.error(f"ID Conflict: {hex(id)} is already {self.reverse_registry[id]}")
             return False

        self.global_registry[concept] = id
        self.reverse_registry[id] = concept
        return True

    def get_standard_id(self, concept: str) -> Optional[int]:
        return self.global_registry.get(concept.lower())

    def define_private_id(self, concept: str) -> int:
        """
        定义私有 ID (自动分配在 Private Range)
        """
        # 简单哈希分配或递增
        # 这里使用确定性哈希映射到 Private Range
        h = hash(concept)
        offset = h % (self.PRIVATE_RANGE[1] - self.PRIVATE_RANGE[0])
        private_id = self.PRIVATE_RANGE[0] + offset
        return private_id

# 单例模式
_registry = RegistryManager()

def get_registry():
    return _registry
