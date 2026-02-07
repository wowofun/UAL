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

        # 3. 绘制
        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 6))
        
        nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=1500, alpha=0.8)
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        
        nx.draw_networkx_edges(G, pos, style=edge_styles, edge_color=edge_colors, 
                             arrows=True, arrowsize=20, width=1.5)
        
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
        
        plt.title(title)
        plt.axis('off')
        plt.savefig(output_file)
        logger.info(f"Graph saved to {output_file}")
        plt.close()

    def generate_preview_html(self, graph_data: Graph, output_file: str = "UAL_Preview.html"):
        """
        生成交互式 HTML 预览 (基于 Mermaid.js)
        """
        mermaid_lines = ["graph TD"]
        
        # 1. Styles
        # IF/Logic: Orange (Diamond)
        # Action: Green (Rect)
        # Entity: Blue (Circle/Rect)
        
        # 2. Nodes
        for node in graph_data.nodes:
            label = self._get_node_label(node).replace('"', "'")
            shape_start = "["
            shape_end = "]"
            
            if node.type == Node.LOGIC:
                shape_start = "{"
                shape_end = "}"
                style_class = "logic"
            elif node.type == Node.ACTION:
                shape_start = "("
                shape_end = ")"
                style_class = "action"
            elif node.type == Node.ENTITY:
                shape_start = "(["
                shape_end = "])"
                style_class = "entity"
            else:
                style_class = "default"
                
            mermaid_lines.append(f'    {node.id}{shape_start}"{label}"{shape_end}:::class_{style_class}')

        # 3. Edges
        relation_map = {
            Edge.DEPENDS_ON: "-->|deps|",
            Edge.NEXT: "-->|next|",
            Edge.ATTRIBUTE: "---|attr|",
            Edge.ARGUMENT: "-->|arg|",
            Edge.CONDITION: "-->|if|",
            Edge.CONSEQUENCE: "-->|then|", # Assuming we add this or map it
            4: "-->|cond|", # Map raw ID if enum not fully updated
            5: "-->|then|"
        }
        
        for edge in graph_data.edges:
            arrow = relation_map.get(edge.relation, "-->")
            mermaid_lines.append(f"    {edge.source_id} {arrow} {edge.target_id}")
            
        mermaid_content = "\n".join(mermaid_lines)
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>UAL Logic Preview</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: sans-serif; padding: 20px; background: #f0f0f0; }}
        .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        .mermaid {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>UAL Visual Debugger</h1>
        <p>Generated Logic Topology</p>
        <div class="mermaid">
{mermaid_content}
        </div>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{ curve: 'basis' }}
        }});
    </script>
</body>
</html>
"""
        with open(output_file, 'w') as f:
            f.write(html_template)
        
        logger.info(f"HTML Preview generated at: {output_file}")
