# Show HN: UAL - An Open Source "Esperanto" for AI Agents (90% Smaller than JSON)

Hi HN,

We just open-sourced **UAL (Universal Agent Language)**, a protocol designed to replace JSON/XML for machine-to-machine communication in the age of Autonomous Agents.

Code: https://github.com/wowofun/UAL (MIT)

### The Problem
If you have a heterogeneous fleet (e.g., a DJI Drone, a KUKA Arm, and a GPT-4 Agent), getting them to talk is a nightmare. You end up with brittle JSON schemas, massive bandwidth usage, and constant parsing errors.

### The Solution: Semantic-First Protocol
Instead of sending strings like `{"action": "move", "target": "kitchen"}`, UAL maps these concepts to a **Universal Atlas** (e.g., `0xA1` = Move). It uses a DAG (Directed Acyclic Graph) structure to build complex logic from simple primitives.

### Performance: UAL vs JSON-RPC
We ran a benchmark on a standard "Navigation Command" payload:

| Metric | JSON-RPC | UAL (v0.2) | Improvement |
| :--- | :--- | :--- | :--- |
| **Payload Size** | ~120 bytes | **12 bytes** | **10x Smaller** |
| **Parsing Time** | ~0.5ms | **~0.02ms** | **25x Faster** |
| **Ambiguity** | High (String matching) | **Zero** (Semantic IDs) | N/A |

### Key Features
1.  **Zero-Shot Definition**: Agents can define new concepts on the fly (e.g., `NOT + HEAR = Silence`).
2.  **Embedded Ready**: We are working on `ual-rs`, a `no_std` Rust implementation for microcontrollers.
3.  **ROS2 Native**: Comes with a gateway node to intercept `/cmd_vel` and inject semantic logic.
4.  **Decentralized Consensus**: Gossip protocol to share new vocabulary across the fleet.

We believe this could be the **TCP/IP for Agentic AI**.

Would love your feedback on the protocol design!

— The UAL Team
