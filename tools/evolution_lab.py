import random
import time
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ual.core import UAL
from ual.atlas import UniversalAtlas

class EvolutionaryLab:
    """
    UAL 语言进化实验室 (Evolutionary Lab)
    
    通过遗传算法模拟 AI 对话，筛选出压缩比最高、效率最高的语义编码。
    """
    
    def __init__(self, generations=5, population_size=10):
        self.generations = generations
        self.population_size = population_size
        self.agent_a = UAL("Evo_Agent_A")
        self.agent_b = UAL("Evo_Agent_B")
        
        # 种子语料库
        self.corpus = [
            "Drone move to target and scan area",
            "Warning battery low return to base",
            "If obstacle detected then hover",
            "Package delivered release payload",
            "System status check speed and position"
        ]
        
    def run_evolution(self):
        print(f"🧬 Starting Evolutionary Lab ({self.generations} generations)...")
        
        best_compression_ratio = 0.0
        best_encoding_strategy = None
        
        for gen in range(self.generations):
            print(f"\n--- Generation {gen + 1} ---")
            
            # 模拟变异: 尝试使用更短的 ID 或组合 (这里模拟为随机优化因子)
            # 在真实实现中，这里会尝试为常用短语分配新的 16-bit 短 ID
            mutation_factor = random.uniform(0.95, 1.05) 
            
            total_original_size = 0
            total_encoded_size = 0
            success_count = 0
            
            for task in self.corpus:
                # 1. 编码
                encoded = self.agent_a.encode(task)
                
                # 模拟进化：随机"压缩"优化
                # 只有当 mutation_factor < 1.0 时模拟发现了更高效的编码
                current_encoded_len = len(encoded)
                if mutation_factor < 1.0:
                    current_encoded_len = int(current_encoded_len * mutation_factor)
                
                # 2. 解码验证
                try:
                    decoded = self.agent_b.decode(encoded)
                    # 简单验证关键词
                    if any(word in decoded['natural_language'] for word in ["move", "scan", "battery", "hover"]):
                        success_count += 1
                except:
                    pass
                
                total_original_size += len(task)
                total_encoded_size += current_encoded_len
                
            # 计算指标
            compression_ratio = (1 - (total_encoded_size / total_original_size)) * 100
            error_rate = 1.0 - (success_count / len(self.corpus))
            
            print(f"   Avg Compression: {compression_ratio:.2f}%")
            print(f"   Success Rate:    {(1-error_rate)*100:.1f}%")
            
            # 优胜劣汰
            if compression_ratio > best_compression_ratio and error_rate == 0:
                best_compression_ratio = compression_ratio
                best_encoding_strategy = mutation_factor
                print("   ✅ New Best Strategy Discovered!")
            else:
                print("   ❌ Strategy Discarded.")
                
        print(f"\n🏆 Evolution Complete. Peak Compression: {best_compression_ratio:.2f}%")
        return best_compression_ratio

if __name__ == "__main__":
    lab = EvolutionaryLab()
    lab.run_evolution()
