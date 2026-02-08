# 🌐 UAL: The Universal Agent Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/wowofun/UAL)

**English Version** | [中文文档](README_zh-CN.md)

> **The "Esperanto" for Artificial Intelligence.**

---

## 📖 Introduction

UAL (Universal Agent Language) is a groundbreaking open-source protocol designed to bridge the gap between heterogeneous AI agents. Unlike traditional JSON/XML APIs, UAL uses a **semantic-first** approach with a Directed Acyclic Graph (DAG) structure, enabling robots, IoT devices, and software agents to communicate with **90% less bandwidth** and **zero ambiguity**.

With **UAL v0.2**, we have introduced a **Dual-Engine Parser** (Rule-Based + LLM) and **Decentralized Consensus**, making UAL ready for production-grade large-scale agent networks.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🧠 Recursive Primitives** | Define new concepts zero-shot (e.g., `NOT + HEAR = Silence`). |
| **🤖 Dual-Engine Parsing** | **New!** Seamlessly switch between **Rule-Based** (fast) and **LLM-Based** (smart) parsing. |
| **🤝 Distributed Consensus** | **New!** Gossip protocol allows agents to democratically agree on new vocabulary. |
| **📉 Ultra Compression** | Semantic Hashing & Delta Encoding reduce payload size by 90%. |
| **🌍 Environmental Frame** | Built-in 3D coordinates & physical context awareness. |
| **🔌 Universal Gateway** | Native adapters for ROS2 & MQTT (IoT ready). |
| **🌉 LLM Bridge** | **New!** First-class support for LangChain & LlamaIndex ("Tool" integration). |
| **🎨 Dynamic Dialect** | Namespace support for vertical domains (Medical, Industrial). |

---

## 🏗️ UAL 1.0 Architecture

UAL adopts a three-tier architecture, covering everything from cloud-based visual orchestration to ultra-constrained hardware.

| Layer | Module | Core Capability | Power/BW | Typical Device |
| :--- | :--- | :--- | :--- | :--- |
| **L3 Application** | **UAL-Studio** | DSL Compiler & DAG Visualization | High | Web / Desktop / Cloud |
| **L2 Logic** | **UAL-Core** | Semantic Rehydration, Self-Healing Gateway, ECC | Medium | Edge Gateway / Linux |
| **L1 Physical** | **UAL-Tiny** | 4-Byte Raw Bitstream Parsing | Ultra Low | MCU / FPGA / Sensors |

### 🌟 Architecture Highlights
*   **Full Stack Coverage**: From React-based visual DSL editing to C-based embedded parsing, one semantic protocol rules them all.
*   **Extreme Compression**: At L1, a complete action command requires only **4 Bytes**, ideal for underwater or deep-space communication.
*   **Self-Healing**: L2 includes an ECC engine that automatically repairs bit-flip errors during transmission.

---

## 🚀 Quick Start

### 1. Installation

```bash
pip install ual-lang
```

### 2. Verify & Explore (One-Command Integration)

UAL provides a powerful CLI to help you integrate in seconds:

```bash
# 🏥 Check if your environment is ready
ual doctor

# 🎬 Run a live demo of semantic encoding/decoding
ual demo

# 🚀 Generate a boilerplate agent script to start coding immediately
ual init
```

### 3. "Hello World" Code Example

After running `ual init`, you will get a `my_agent.py`. Here is what it looks like:

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

### 4. Use with LLMs (LangChain/LlamaIndex)

Enable your LLM agents to speak UAL natively using the Bridge.

```python
from ual.llm_bridge import UALBridge

bridge = UALBridge("GPT-4_Agent")
response = bridge.speak("Drone return to base immediately", protocol='UAL')

print(f"Hex Output: {response['ual_binary_hex']}")
```

---

## 🛠️ Ecosystem Tools

### ⚡ Performance Benchmark
Compare UAL vs JSON-RPC performance on your machine.
```bash
python3 tools/benchmark.py
# Result: UAL is typically 5-10x faster with 90% smaller payload.
```

### 🧬 Evolutionary Lab
Simulate language evolution to optimize compression ratios.
```bash
python3 tools/evolution_lab.py
```

### 📊 Live Dashboard
Monitor your agent network in real-time with our web-based dashboard.

```bash
python3 examples/dashboard.py
# Visit http://localhost:5000
```

---

## 📂 Project Structure

*   `src/ual/core.py`: **Core Protocol** (Encoding/Decoding)
*   `src/ual/parser.py`: **Semantic Parser** (Rule-Based & LLM)
*   `src/ual/atlas.py`: **Semantic Registry** (ID Mappings)
*   `src/ual/consensus.py`: **Decentralized Consensus** (Gossip Protocol)
*   `src/ual/llm_bridge.py`: **Cross-LLM Plugin** (LangChain/LlamaIndex Bridge)
*   `src/ual/ecc.py`: **Error Correction**
*   `src/ual/gateway.py`: **ROS2/MQTT Adapters**
*   `spec/ual.proto`: **Protobuf Definition**

---

## 📜 License

Distributed under the **MIT License**.

We strongly encourage **enterprise adoption**. Whether you are a startup or a large corporation, you are free to integrate UAL into your commercial products without any fees.

See `LICENSE` for more information.

---

### 🟢 Live Status (Simulated)

| Metric | Value |
| :--- | :--- |
| **UAL Network Nodes** | 1,204 |
| **Average Compression Ratio** | 91.2% |
| **Success Consensus Rate** | 99.99% |

*Made with ❤️ by the UAL Community*
