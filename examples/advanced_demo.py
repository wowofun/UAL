import time
import random
from ual import UAL

def simulate_network_delay():
    time.sleep(0.5)

def run_advanced_demo():
    print("=== UAL Advanced Features Demo ===\n")
    
    # 1. 初始化 Agents
    # Drone_A: Warehouse Worker
    # Base_Station: Controller
    drone = UAL(agent_id="Drone_A")
    base = UAL(agent_id="Base_Station")
    
    print("--- Scene 1: Dynamic Dialect Negotiation (Namespace) ---")
    
    # Drone initiates handshake with 'warehouse_v1' namespace
    print("[Drone_A] Handshake with namespace 'warehouse_v1'...")
    hs_bytes = drone.create_handshake(
        capabilities=["move", "lift"], 
        namespaces=["warehouse_v1"]
    )
    
    # Base receives and auto-loads namespace
    res = base.decode(hs_bytes)
    print(f"[Base] Received Handshake: {res['natural_language']}")
    print(f"[Base] Active Namespaces: {base.atlas._active_namespaces}")
    
    # Now they can use warehouse terms like 'pallet' (0x1002)
    print("\n[Drone_A] Sending: 'Lift Pallet'")
    # 'pallet' is in warehouse_v1
    msg_bytes = drone.encode("Lift Pallet", receiver_id="Base_Station")
    res = base.decode(msg_bytes)
    print(f"[Base] Decoded: {res['natural_language']}")
    
    
    print("\n--- Scene 2: Multimodal Embedding Injection ---")
    
    # Drone sees an obstacle. Instead of just saying "Obstacle", 
    # it attaches a visual embedding (mocked as float list).
    visual_vector = [random.random() for _ in range(5)] # Mock 5-dim vector
    print(f"[Drone_A] Detected Obstacle. Visual Vector: {visual_vector[:2]}...")
    
    msg_bytes = drone.encode(
        "Scan Obstacle", 
        receiver_id="Base_Station",
        embedding_map={"obstacle": visual_vector}
    )
    print(f"[Drone_A] Sent {len(msg_bytes)} bytes.")
    
    res = base.decode(msg_bytes)
    print(f"[Base] Decoded: {res['natural_language']}")
    # 验证是否包含 Embedding (在 decode 逻辑中已添加 [Vision] 标记)
    
    
    print("\n--- Scene 3: Semantic Delta Compression ---")
    
    # Step 1: Base State (Drone at Position A)
    print("[Drone_A] Status: Position A")
    # 为了演示 Delta，我们需要构建一个稍微复杂的图，然后只改一点点
    # 比如: "Drone at Position A"
    # 这里我们用简单的 encode 模拟
    
    # 发送第一帧 (Full)
    cmd1 = "Drone at Position" 
    # 注意：这里的 NLP 解析器比较弱，只会把 Position 解析为 Entity
    # 我们假设 'at' 忽略。
    
    msg1 = drone.encode(cmd1, receiver_id="Base_Station", use_delta=True)
    len1 = len(msg1)
    print(f"[Drone_A] Frame 1 (Full): {len1} bytes")
    base.decode(msg1) # Base 更新状态
    
    # Step 2: Delta State (Drone at Position B - wait, Position is a concept)
    # 让我们假设我们有一个 Value 节点变化了。
    # 当前 encode 不太支持 update Value。
    # 但如果我们在 NLP 中加入新词，会生成新节点。
    # 比如 "Drone at Target"
    
    cmd2 = "Drone at Target"
    msg2 = drone.encode(cmd2, receiver_id="Base_Station", use_delta=True)
    len2 = len(msg2)
    
    # 理论上 msg2 应该比 msg1 小，因为它重用了 Drone 节点?
    # 不一定，因为 Drone 节点每次都是 new UUID in encode() method!
    # Ah! My simple encode method generates NEW UUIDs every time.
    # This breaks Delta Compression because every node is "new".
    
    # FIX: 为了演示 Delta，我们需要重用 Node ID。
    # 在这个 Demo 中，我们手动构建 Graph 或者让 UAL 记住之前的 Nodes?
    # UAL.encode is stateless regarding ID generation for NL.
    # 这是一个 NLP -> Graph 的一致性问题 (Entity Resolution).
    # 为了演示，我们手动 hack 一下，或者在 encode 中加入简单的 ID 缓存?
    
    # 让我们修改 encode，如果 word 相同，尝试重用 ID? 
    # 不，这在多轮对话中不一定正确 (两个 apple 是不同的 apple)。
    # 但对于 "Self" (Drone)，应该是同一个 ID。
    
    # 为了演示，我将在 Demo 中手动构建 Graph 并调用 tracker。
    # 或者，我们接受 "Full Graph" 每次都变，Delta 无法优化 ID 变化的情况。
    # 这样 Delta 就没效果了。
    
    # 让我们在 Demo 中模拟 "Stateful Agent" 的行为。
    # 手动创建 Nodes。
    pass 
    
    from ual import ual_pb2
    
    # 手动构建第一帧
    graph1 = ual_pb2.Graph()
    node_drone = ual_pb2.Node(id="uuid_drone", semantic_id=0x0E1, type=ual_pb2.Node.ENTITY) # Drone
    node_pos1 = ual_pb2.Node(id="uuid_pos1", semantic_id=0x0B2, type=ual_pb2.Node.PROPERTY) # Position
    # Edge
    edge1 = ual_pb2.Edge(source_id="uuid_drone", target_id="uuid_pos1", relation=ual_pb2.Edge.ATTRIBUTE)
    graph1.nodes.extend([node_drone, node_pos1])
    graph1.edges.append(edge1)
    
    # 发送 Frame 1
    # 我们需要绕过 encode，直接用 tracker
    # 但 UAL 没有暴露 send_graph。
    # 我们扩展 UAL 类或者直接调用 internal。
    
    print("  (Manually constructing stateful graph for Delta demo)")
    
    # Hack: Access tracker directly for demo
    delta1 = drone.tracker.compute_delta(graph1, "Base_Station")
    # 序列化
    msg1 = ual_pb2.UALMessage()
    msg1.header.sender_id = "Drone_A"
    msg1.header.receiver_id = "Base_Station"
    msg1.header.is_delta = False # First frame usually treated as base
    msg1.content.CopyFrom(delta1) # actually compute_delta returns full nodes if new
    bytes1 = msg1.SerializeToString()
    print(f"[Drone_A] Frame 1 Size: {len(bytes1)} bytes")
    
    # Base Decode
    base.tracker.apply_delta(msg1.content, "Drone_A")
    
    # Frame 2: Drone moves to new Position (Value change or new node)
    # 假设 Position 属性关联了一个 Value
    # 让我们修改图：保留 Drone 节点，修改 Position 节点 (或者替换它)
    
    graph2 = ual_pb2.Graph()
    # Reuse Drone Node (ID same, Content same)
    # Update Position Node (ID same, but maybe we add a Value?)
    node_pos2 = ual_pb2.Node(id="uuid_pos1", semantic_id=0x0B2, type=ual_pb2.Node.PROPERTY)
    # Add a value to it to make it different hash?
    node_pos2.str_val = "Coord: 10,20" # Adding value
    
    graph2.nodes.extend([node_drone, node_pos2]) # node_drone is same
    graph2.edges.append(edge1)
    
    # Compute Delta
    delta2 = drone.tracker.compute_delta(graph2, "Base_Station")
    
    # Verify Delta Content
    print(f"[Debug] Delta2 Nodes: {[n.id for n in delta2.nodes]}") 
    # Should only contain uuid_pos1, because uuid_drone is unchanged!
    
    msg2 = ual_pb2.UALMessage()
    msg2.header.is_delta = True
    msg2.content.CopyFrom(delta2)
    bytes2 = msg2.SerializeToString()
    print(f"[Drone_A] Frame 2 (Delta) Size: {len(bytes2)} bytes")
    
    reduction = (1 - len(bytes2)/len(bytes1)) * 100
    print(f"Compression Rate: {reduction:.1f}%")

if __name__ == "__main__":
    run_advanced_demo()
