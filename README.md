# UAL (Universal Agent Language / 通用智能体语言)

## 1. 项目愿景 (Vision)

**核心目标**：建立一个开源、跨平台、极高压缩比的 AI 原生通信协议。让全球不同架构的机器人与智能体能够像人类使用英语一样，通过一种逻辑严密、无歧义的“机器母语”进行即时协作。

UAL 旨在解决异构智能体之间的通信壁垒，通过语义编码架构 (Semantic Core) 和语义映射表 (Universal Atlas)，实现高效、精准的信息传递。

## 2. 技术规格 (Technical Specifications)

*   **语义编码**: 采用 Protocol Buffers 封装为有向无环图 (DAG)，摆脱线性文本束缚。
*   **Universal Atlas**: 标准化 ID 映射 (e.g., 0xA1 = Move)，支持动态扩展。
*   **极高压缩**: 语义哈希与 Delta Encoding (已实现)。
*   **多模态支持**: 支持 CLIP/DINOv2 向量嵌入 (已实现)。
*   **动态方言**: 支持命名空间与行业字典协商 (已实现)。
*   **可视化**: 支持拓扑图生成与不确定性 (Probability Cloud) 可视化 (已实现)。
*   **全场景通用**: 
    *   **递归语义元**: 支持 Zero-shot 概念定义 (e.g., I + WANT + NOT = Refuse) (已实现)。
    *   **环境共鸣**: 内置 3D 坐标系与物理环境引用 (已实现)。
    *   **情感向量**: 支持 Urgency 与语气 (Command/Suggestion) 标记 (已实现)。
    *   **自我进化**: 集成 LLM 自动翻译插件，动态扩展词汇 (已实现)。
*   **安全**: 内置签名验证与指令沙箱机制。

## 3. 安装 (Installation)

### 前置要求
*   Python 3.8+
*   Protobuf Compiler (可选，已包含生成的代码)

### 安装步骤

1. 克隆仓库:
   ```bash
   git clone https://github.com/wowofun/UAL.git
   cd UAL
   ```

2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   # 注意: 可视化功能需要 matplotlib
   ```

3. (可选) 重新编译协议:
   ```bash
   python3 -m grpc_tools.protoc -I spec --python_out=src/ual spec/ual.proto
   ```

## 4. 快速开始 (Hello World)

以下示例展示了如何将自然语言指令压缩为 UAL 二进制并还原。

```python
from ual import UAL

# 初始化智能体
agent = UAL(agent_id="Agent_001")

# 1. 握手 (Handshake)
handshake_msg = agent.create_handshake(capabilities=["ual_v1", "move"])
# 发送 handshake_msg 给其他 Agent...

# 2. 编码: 自然语言 -> UAL Binary
command = "Drone move to Target"
binary_data = agent.encode(command)
print(f"Encoded size: {len(binary_data)} bytes")

# 3. 解码: UAL Binary -> 结构化语义
receiver = UAL(agent_id="Agent_002")
result = receiver.decode(binary_data)

print(f"Meaning: {result['natural_language']}")
# Output: Meaning: move drone target
```

## 5. 示例 Demo

*   **基础通信**: `python3 examples/drone_demo.py` (无人机协同)
*   **进阶特性**: `python3 examples/advanced_demo.py` (增量压缩与多模态)
*   **可视化与不确定性**: `python3 examples/visualizer_demo.py` (概率云可视化)
*   **全场景通用性**: `python3 examples/generalization_demo.py` (递归语义与自我进化)

该示例模拟了两个无人机 (Leader/Follower) 之间的通信日志，展示了握手、任务分配、状态同步等过程。

## 6. 项目结构

*   `/spec`: Protocol Buffers 协议定义 (`ual.proto`)
*   `/src`: 核心源代码 (Python 实现)
    *   `core.py`: 编解码逻辑 (Encode/Decode/Validate)
    *   `atlas.py`: 语义映射表与动态命名空间
    *   `state.py`: 状态追踪与增量压缩 (StateTracker)
    *   `primitives.py`: 递归语义元定义
    *   `translator.py`: 自动翻译插件 (SDK 自我进化)
    *   `visualizer.py`: 拓扑可视化工具
    *   `cli.py`: 命令行调试工具
*   `/examples`: 示例代码

---
*License: MIT*
