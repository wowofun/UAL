# 🌐 UAL: 通用智能体语言 (Universal Agent Language)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/wowofun/UAL)

[English Version](README.md) | **中文文档**

> **AI 智能体界的“世界语”。**  
> **The "Esperanto" for Artificial Intelligence.**

---

## 📖 项目简介

UAL (通用智能体语言) 是一个突破性的开源协议，旨在打破不同 AI 智能体之间的通信壁垒。与传统的 JSON/XML API 不同，UAL 采用**语义优先**的 DAG（有向无环图）结构，使机器人、IoT 设备和软件智能体能够以**节省 90% 带宽**的方式进行**零歧义**沟通。

---

## ✨ 核心特性

| 特性 | 说明 |
| :--- | :--- |
| **🧠 递归语义元** | 支持零样本定义新概念 (如 `不 + 听 = 沉默`)。 |
| **📉 极致压缩** | 语义哈希与增量编码可减少 90% 的载荷大小。 |
| **🌍 环境共鸣** | 内置 3D 坐标系与物理环境感知能力。 |
| **🔌 万能网关** | 原生支持 ROS2 与 MQTT 适配，即插即用。 |
| **🛡️ 自动纠错** | ECC 纠错码确保在噪声网络中的通信健壮性。 |
| **🎨 动态方言** | 支持特定领域（医疗、工业）的命名空间扩展。 |

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/wowofun/UAL.git
cd UAL

# 安装依赖
pip install -r requirements.txt
```

### 2. "The Great Demo" 全场景演示

为了证明 UAL 的通用性，我们准备了一个脚本，同时模拟三个截然不同的场景：**智能家居**、**工业工厂**和**抽象辩论**。

```bash
python3 examples/the_great_demo.py
```

### 3. "Hello World" 代码示例

```python
from ual import UAL

# 初始化智能体
sender = UAL("Robot_A")
receiver = UAL("Robot_B")

# 1. 编码: 自然语言 -> 紧凑二进制
cmd = "Move to Kitchen and clean the floor"
binary = sender.encode(cmd)

print(f"📦 Payload Size: {len(binary)} bytes")

# 2. 解码: 紧凑二进制 -> 结构化语义
msg = receiver.decode(binary)
print(f"📩 Received: {msg['natural_language']}")
```

---

## 🛠️ 生态工具

### 📊 实时监控看板
使用基于 Web 的仪表盘实时监控您的智能体网络。

```bash
python3 examples/dashboard.py
# 访问 http://localhost:5000
```

### 📘 自动文档生成
基于当前代码库生成最新的 API 参考文档。

```bash
python3 tools/doc_gen.py
```

---

## 📂 项目结构

*   `src/ual/core.py`: **核心协议** (编解码逻辑)
*   `src/ual/atlas.py`: **语义注册表** (ID 映射)
*   `src/ual/ecc.py`: **纠错机制**
*   `src/ual/gateway.py`: **网关适配器** (ROS2/MQTT)
*   `spec/ual.proto`: **协议定义文件**

---

## 📜 开源协议

本项目基于 **MIT 许可证** 开源。

我们强烈鼓励**企业级引用**与商业化应用。无论是初创公司还是大型企业，您都可以自由地将 UAL 集成到您的商业产品中，无需支付任何费用。

详细协议内容请参阅 [LICENSE](LICENSE) 文件。

---

*Made with ❤️ by the UAL Community*
