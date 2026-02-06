# 🌐 UAL: The Universal Agent Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/wowofun/UAL)

> **The "Esperanto" for Artificial Intelligence.**  
> **AI 智能体界的“世界语”。**

---

## 📖 Introduction / 项目简介

**English**:  
UAL (Universal Agent Language) is a groundbreaking open-source protocol designed to bridge the gap between heterogeneous AI agents. Unlike traditional JSON/XML APIs, UAL uses a **semantic-first** approach with a Directed Acyclic Graph (DAG) structure, enabling robots, IoT devices, and software agents to communicate with **90% less bandwidth** and **zero ambiguity**.

**中文**:  
UAL (通用智能体语言) 是一个突破性的开源协议，旨在打破不同 AI 智能体之间的通信壁垒。与传统的 JSON/XML API 不同，UAL 采用**语义优先**的 DAG（有向无环图）结构，使机器人、IoT 设备和软件智能体能够以**节省 90% 带宽**的方式进行**零歧义**沟通。

---

## ✨ Key Features / 核心特性

| Feature | Description (English) | 说明 (中文) |
| :--- | :--- | :--- |
| **🧠 Recursive Primitives** | Define new concepts zero-shot (e.g., `NOT + HEAR = Silence`). | **递归语义元**: 支持零样本定义新概念 (如 `不 + 听 = 沉默`)。 |
| **📉 Ultra Compression** | Semantic Hashing & Delta Encoding reduce payload size by 90%. | **极致压缩**: 语义哈希与增量编码可减少 90% 的载荷大小。 |
| **🌍 Environmental Frame** | Built-in 3D coordinates & physical context awareness. | **环境共鸣**: 内置 3D 坐标系与物理环境感知能力。 |
| **🔌 Universal Gateway** | Native adapters for ROS2 & MQTT (IoT ready). | **万能网关**: 原生支持 ROS2 与 MQTT 适配，即插即用。 |
| **🛡️ Self-Correction** | Error Correction Code (ECC) ensures robustness in noisy networks. | **自动纠错**: ECC 纠错码确保在噪声网络中的通信健壮性。 |
| **🎨 Dynamic Dialect** | Namespace support for vertical domains (Medical, Industrial). | **动态方言**: 支持特定领域（医疗、工业）的命名空间扩展。 |

---

## 🚀 Quick Start / 快速开始

### 1. Installation / 安装

```bash
# Clone the repository / 克隆仓库
git clone https://github.com/wowofun/UAL.git
cd UAL

# Install dependencies / 安装依赖
pip install -r requirements.txt
```

### 2. The "Great Demo" / 全场景演示

To prove UAL's universality, we have prepared a single script that simulates three distinct scenarios: **Smart Home**, **Industrial Factory**, and **Abstract Debate**.
为了证明 UAL 的通用性，我们准备了一个脚本，同时模拟三个截然不同的场景：**智能家居**、**工业工厂**和**抽象辩论**。

```bash
python3 examples/the_great_demo.py
```

### 3. "Hello World" Code / 代码示例

```python
from ual import UAL

# Initialize Agents / 初始化智能体
sender = UAL("Robot_A")
receiver = UAL("Robot_B")

# 1. Encode Command (Natural Language -> Compact Binary)
# 编码: 自然语言 -> 紧凑二进制
cmd = "Move to Kitchen and clean the floor"
binary = sender.encode(cmd)

print(f"📦 Payload Size: {len(binary)} bytes")

# 2. Decode (Compact Binary -> Structured Logic)
# 解码: 紧凑二进制 -> 结构化语义
msg = receiver.decode(binary)
print(f"📩 Received: {msg['natural_language']}")
```

---

## 🛠️ Ecosystem Tools / 生态工具

### 📊 Live Dashboard / 实时监控看板
Monitor your agent network in real-time with our web-based dashboard.
使用基于 Web 的仪表盘实时监控您的智能体网络。

```bash
python3 examples/dashboard.py
# Visit http://localhost:5000
```

### 📘 Auto-Documentation / 自动文档生成
Generate the latest API reference based on your current codebase.
基于当前代码库生成最新的 API 参考文档。

```bash
python3 tools/doc_gen.py
```

---

## 📂 Project Structure / 项目结构

*   `src/ual/core.py`: **Core Protocol** (Encoding/Decoding) / 核心协议
*   `src/ual/atlas.py`: **Semantic Registry** (ID Mappings) / 语义注册表
*   `src/ual/ecc.py`: **Error Correction** / 纠错机制
*   `src/ual/gateway.py`: **ROS2/MQTT Adapters** / 网关适配器
*   `spec/ual.proto`: **Protobuf Definition** / 协议定义文件

---

## 📜 License / 许可证

Distributed under the MIT License. See `LICENSE` for more information.
本项目基于 MIT 许可证开源。

---

*Made with ❤️ by the UAL Community*
