import logging
from typing import Optional, Dict
from .ual_pb2 import Graph, Node, Edge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoTranslator:
    """
    UAL Auto-Translator Plugin (SDK Self-Evolution)
    自动将未知的自然语言映射为 UAL 逻辑图。
    """
    
    def __init__(self, atlas, llm_provider=None):
        self.atlas = atlas
        self.llm_provider = llm_provider # Interface for LLM (e.g., OpenAI, Gemini)
        self.cache: Dict[str, Graph] = {}

    def translate(self, unknown_text: str) -> Optional[Graph]:
        """
        尝试翻译未知文本。
        1. 查缓存
        2. 调用 LLM (Mock)
        3. 缓存结果到 Atlas 用户扩展区
        """
        # 1. Check Cache
        if unknown_text in self.cache:
            logger.info(f"Cache hit for '{unknown_text}'")
            return self.cache[unknown_text]
        
        # 2. Call LLM (Mock implementation)
        logger.info(f"Translating unknown term: '{unknown_text}' via LLM...")
        graph = self._mock_llm_translation(unknown_text)
        
        if graph:
            # 3. Cache & Register
            self.cache[unknown_text] = graph
            # Assign a dynamic ID in User Extension Range (0xF000+)
            new_id = 0xF000 + len(self.cache)
            self.atlas.register_dynamic_concept(new_id, unknown_text)
            logger.info(f"Learned new concept: '{unknown_text}' -> ID {hex(new_id)}")
            
        return graph

    def _mock_llm_translation(self, text: str) -> Optional[Graph]:
        """
        模拟 LLM 返回的结构化图。
        In production, this would parse LLM JSON output to Graph.
        """
        # 模拟：如果输入是 "Collaborate" (协作)
        if "collaborate" in text.lower():
            # LLM 分解：Collaborate = WORK + TOGETHER
            # 这里简化返回一个 Graph
            g = Graph()
            # Node 1: Work (Action)
            n1 = Node(id="n1", type=Node.ACTION, semantic_id=0x040) # DO/WORK
            # Node 2: Together (Adverb/Property) - Mock ID
            n2 = Node(id="n2", type=Node.PROPERTY, str_val="together")
            
            e1 = Edge(source_id="n1.id", target_id="n2.id", relation=Edge.ATTRIBUTE)
            
            g.nodes.extend([n1, n2])
            g.edges.append(e1)
            return g
            
        return None
