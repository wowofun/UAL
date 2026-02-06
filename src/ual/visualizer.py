import networkx as nx
import logging
from .ual_pb2 import Graph, Node, Edge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("Matplotlib not found. Visualization will be disabled.")

class UALVisualizer:
    """
    UAL 可视化器
    将 UAL 二进制/Graph 对象转化为人类可读的拓扑图。
    支持显示概率分布云 (Uncertainty Clouds)。
    """

    def __init__(self, atlas=None):
        self.atlas = atlas
        self.node_colors = {
            Node.ENTITY: 'lightblue',
            Node.ACTION: 'lightgreen',
            Node.PROPERTY: 'yellow',
            Node.LOGIC: 'orange',
            Node.MODAL: 'pink',
            Node.VALUE: 'lightgrey',
            Node.DATA_REF: 'violet',
            Node.UNKNOWN: 'white'
        }

    def _get_node_label(self, node: Node) -> str:
        """获取节点显示标签"""
        # 1. 优先使用具体的 Value
        if node.HasField("str_val"):
            return f"{node.str_val}"
        elif node.HasField("num_val"):
            return f"{node.num_val}"
        elif node.HasField("bool_val"):
            return str(node.bool_val)
        
        # 2. 使用 Atlas 解析 Semantic ID
        if self.atlas:
            concept = self.atlas.get_concept(node.semantic_id)
            if concept:
                return concept
        
        # 3. 降级显示 ID
        return f"Node_{node.id[:4]}"

    def visualize(self, graph_data: Graph, title: str = "UAL Topology", output_file: str = "ual_graph.png"):
        """
        生成拓扑图并保存为图片
        """
        if not HAS_MATPLOTLIB:
            logger.error("Cannot visualize: Matplotlib is not installed.")
            return

        G = nx.DiGraph()
        labels = {}
        colors = []
        edge_labels = {}
        edge_colors = []
        edge_styles = []

        # 1. 添加节点
        for node in graph_data.nodes:
            G.add_node(node.id)
            labels[node.id] = self._get_node_label(node)
            colors.append(self.node_colors.get(node.type, 'white'))

        # 2. 添加边 (处理不确定性)
        for edge in graph_data.edges:
            G.add_edge(edge.source_id, edge.target_id)
            
            # 概率处理
            weight = edge.weight if edge.weight > 0 else 1.0
            confidence_text = f"{weight*100:.0f}%" if weight < 1.0 else ""
            
            relation_map = {
                Edge.DEPENDS_ON: "deps",
                Edge.NEXT: "next",
                Edge.ATTRIBUTE: "attr",
                Edge.ARGUMENT: "arg",
                Edge.CONDITION: "cond"
            }
            rel_name = relation_map.get(edge.relation, "?")
            
            if confidence_text:
                edge_labels[(edge.source_id, edge.target_id)] = f"{rel_name}\n({confidence_text})"
                edge_styles.append('dashed') # 不确定连接用虚线
                edge_colors.append((0, 0, 0, weight)) # 透明度随置信度变化
            else:
                edge_labels[(edge.source_id, edge.target_id)] = rel_name
                edge_styles.append('solid')
                edge_colors.append('black')

        # 3. 绘图
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, k=1.5) # 弹簧布局
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=2000, alpha=0.9, edgecolors='gray')
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, style=edge_styles, arrowsize=20, width=2)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        plt.title(title)
        plt.axis('off')
        
        try:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Graph visualization saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save visualization: {e}")
        finally:
            plt.close()
