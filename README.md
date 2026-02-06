# 🌐 UAL: The Universal Agent Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/wowofun/UAL)

**English Version** | [中文文档](README_zh-CN.md)

> **The "Esperanto" for Artificial Intelligence.**

---

## 📖 Introduction

UAL (Universal Agent Language) is a groundbreaking open-source protocol designed to bridge the gap between heterogeneous AI agents. Unlike traditional JSON/XML APIs, UAL uses a **semantic-first** approach with a Directed Acyclic Graph (DAG) structure, enabling robots, IoT devices, and software agents to communicate with **90% less bandwidth** and **zero ambiguity**.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🧠 Recursive Primitives** | Define new concepts zero-shot (e.g., `NOT + HEAR = Silence`). |
| **📉 Ultra Compression** | Semantic Hashing & Delta Encoding reduce payload size by 90%. |
| **🌍 Environmental Frame** | Built-in 3D coordinates & physical context awareness. |
| **🔌 Universal Gateway** | Native adapters for ROS2 & MQTT (IoT ready). |
| **🛡️ Self-Correction** | Error Correction Code (ECC) ensures robustness in noisy networks. |
| **🎨 Dynamic Dialect** | Namespace support for vertical domains (Medical, Industrial). |

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/wowofun/UAL.git
cd UAL

# Install dependencies
pip install -r requirements.txt
```

### 2. The "Great Demo"

To prove UAL's universality, we have prepared a single script that simulates three distinct scenarios: **Smart Home**, **Industrial Factory**, and **Abstract Debate**.

```bash
python3 examples/the_great_demo.py
```

### 3. "Hello World" Code

```python
from ual import UAL

# Initialize Agents
sender = UAL("Robot_A")
receiver = UAL("Robot_B")

# 1. Encode Command (Natural Language -> Compact Binary)
cmd = "Move to Kitchen and clean the floor"
binary = sender.encode(cmd)

print(f"📦 Payload Size: {len(binary)} bytes")

# 2. Decode (Compact Binary -> Structured Logic)
msg = receiver.decode(binary)
print(f"📩 Received: {msg['natural_language']}")
```

---

## 🛠️ Ecosystem Tools

### 📊 Live Dashboard
Monitor your agent network in real-time with our web-based dashboard.

```bash
python3 examples/dashboard.py
# Visit http://localhost:5000
```

### 📘 Auto-Documentation
Generate the latest API reference based on your current codebase.

```bash
python3 tools/doc_gen.py
```

---

## 📂 Project Structure

*   `src/ual/core.py`: **Core Protocol** (Encoding/Decoding)
*   `src/ual/atlas.py`: **Semantic Registry** (ID Mappings)
*   `src/ual/ecc.py`: **Error Correction**
*   `src/ual/gateway.py`: **ROS2/MQTT Adapters**
*   `spec/ual.proto`: **Protobuf Definition**

---

## 📜 License

Distributed under the **MIT License**.

We strongly encourage **enterprise adoption**. Whether you are a startup or a large corporation, you are free to integrate UAL into your commercial products without any fees.

See `LICENSE` for more information.

---

*Made with ❤️ by the UAL Community*
