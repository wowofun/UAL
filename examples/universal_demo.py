import argparse
import yaml
from ual import UAL  # 假设你的核心模块
from ual.atlas import get_atlas
try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError:
    nx = None
    plt = None
    print("⚠️ Visualization modules (networkx, matplotlib) not found. Visualization disabled.")

def load_config(config_path: str = None) -> dict:
    """加载 YAML 配置，定义时空和任务"""
    default_config = {
        "space": {  # 空间设置
            "frame_id": "universal_frame",
            "origin": [0.0, 0.0, 0.0],  # [x, y, z] 或扩展到 [x, y, z, t]
            "orientation": [0.0, 0.0, 0.0, 1.0],  # 四元数
            "unit": "meter"  # 可换 "second", "pixel", "abstract_unit"
        },
        "time": {  # 时间设置
            "start_timestamp": 0,  # Unix 或自定义
            "duration": "infinite",  # 或 "10s", "1day"
            "mode": "real_time"  # "simulation", "historical", "predictive"
        },
        "tasks": [  # 任务列表，NL 输入
            "Move to target in 3D space",
            "If obstacle then hover and scan",
            "Debate: What is the meaning of life?"
        ],
        "namespaces": ["warehouse_v1", "medical_v1"]  # 动态加载方言
    }
    
    if config_path:
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            print(f"📄 User config content: {user_config}")
            if user_config:
                default_config.update(user_config)
    
    return default_config

def visualize_dag(nodes, edges):
    """可视化 DAG 图（可选，用于 debug）"""
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node.id, label=f"{node.semantic_id:X} ({get_atlas().get_concept(node.semantic_id)})")
    for edge in edges:
        G.add_edge(edge.source_id, edge.target_id, label=edge.relation)
    
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue')
    plt.show()  # 或 savefig

def run_universal_demo(config: dict):
    atlas = get_atlas()
    
    # 激活命名空间
    for ns in config["namespaces"]:
        atlas.load_namespace(ns)
    
    # 初始化代理
    agent = UAL("Universal_Agent")
    
    # 设置环境帧
    env_frame = agent.create_env_frame(**config["space"])  # 假设 UAL 有此方法；否则手动建 Header
    
    for task in config["tasks"]:
        print(f"🚀 执行通用任务: {task}")
        
        # 解析 NL → DAG
        nodes, edges, metadata = agent.parse(task)  # 假设 parse 方法返回三元组
        
        # 注入时空
        metadata["env_frame"] = env_frame
        metadata["timestamp"] = config["time"]["start_timestamp"]
        
        # 编码 + 模拟执行
        binary = agent.encode_from_graph(nodes, edges, metadata)
        print(f"📦 编码大小: {len(binary)} bytes")
        
        # 解码验证
        decoded = agent.decode(binary)
        print(f"📩 解码结果: {decoded['natural_language']}")
        
        # 可视化（可选）
        # visualize_dag(nodes, edges)
        
        # 模拟执行（简单状态机示例）
        current_state = {"position": config["space"]["origin"]}
        for node in nodes:  # 简化执行
            concept = atlas.get_concept(node.semantic_id)
            if concept == "move":
                current_state["position"] = [x + 1 for x in current_state["position"]]  # 模拟移动
        print(f"🌌 模拟后状态: {current_state}")

if __name__ == "__main__":
    try:
        print("🔍 Starting Universal Demo...")
        parser = argparse.ArgumentParser(description="UAL 通用场景 Demo")
        parser.add_argument("--config", type=str, help="YAML 配置路径")
        args = parser.parse_args()
        
        print(f"📂 Loading config from: {args.config}")
        config = load_config(args.config)
        print(f"🔧 Config loaded: {config.keys()}")
        run_universal_demo(config)
        print("✅ Demo completed successfully.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error: {e}")