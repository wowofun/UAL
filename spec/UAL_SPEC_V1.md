# UAL Protocol Specification Version 1.0 (Draft)

**Status**: Request for Comments (RFC)
**Date**: 2026-02-07
**Author**: UAL Working Group
**Category**: Standards Track

---

## Abstract

Universal Action Language (UAL) is a binary-first, semantic protocol designed for inter-agent communication in distributed autonomous systems. Unlike text-based protocols (JSON, XML), UAL prioritizes compactness, logical determinism, and execution speed. This document specifies the version 1.0 wire format, the semantic consensus mechanism, and the hashing algorithms required for compliance.

## 1. Introduction

The current landscape of Machine-to-Machine (M2M) communication is dominated by human-readable formats. While useful for debugging, these formats introduce significant overhead (serialization/deserialization costs, bandwidth usage) and ambiguity. UAL addresses these issues by defining a rigid 3-byte instruction unit and a dynamic, cryptographically verifiable dictionary (The Atlas).

## 2. Binary Wire Format

A UAL packet consists of a fixed-size header followed by a variable-length payload of 3-byte Semantic Units (SU).

### 2.1. Packet Header (32 bits)

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Ver  | Type  |    Reserved   |         Payload Length        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

*   **Ver (4 bits)**: Protocol Version. Current value: `0x1`.
*   **Type (4 bits)**: Packet Type.
    *   `0x0`: Command (Action Request)
    *   `0x1`: Query (State Request)
    *   `0x2`: Response (Ack/Nack/Data)
    *   `0x3`: Consensus (Atlas Update Vote)
*   **Reserved (8 bits)**: Must be zero. Reserved for future QoS flags.
*   **Payload Length (16 bits)**: Length of the payload in bytes (max 65535 bytes).

### 2.2. Semantic Unit (SU)

The payload is a sequence of 3-byte SUs.

```text
[ Category (8 bits) ] [ ID (16 bits) ]
```

*   **Category**: Defines the namespace (e.g., `0xA0` = Action, `0xE0` = Entity).
*   **ID**: The specific semantic token index within that category.

## 3. The Consensus Layer

UAL allows the dictionary (Atlas) to evolve. Agents can propose new semantic definitions.

### 3.1. Proposal Mechanism
An agent proposing a new term broadcasts a `Type 0x3` packet containing:
1.  **Proposed Definition**: A machine-readable definition (e.g., composed of existing primitives).
2.  **Proposed Hex**: A suggested 3-byte code.
3.  **Proof of Work (PoW)**: A nonce ensuring the hash of the definition meets a difficulty target (preventing spam).

### 3.2. Voting
Network participants vote to accept the new term based on:
*   **Uniqueness**: Does it conflict with existing terms?
*   **Utility**: Is it composed of valid primitives?

If >51% of local neighbors accept, the term is added to the temporary "MemPool" Atlas.

## 4. Semantic Hashing

To ensure that "Scan Area" means the same thing to a drone in Tokyo and a rover on Mars, UAL uses **Semantic Hashing**.

### 4.1. Algorithm
The unique ID for any complex concept is derived from its definition graph.

```python
def semantic_hash(concept_graph):
    # 1. Canonicalize the DAG (topological sort of nodes)
    canonical_str = serialize_graph(concept_graph)
    
    # 2. SHA-256 Hash
    full_hash = sha256(canonical_str)
    
    # 3. Truncate to 16 bits for the ID part
    # (Collision handling: probing with incremented nonce)
    return full_hash[:2] 
```

This ensures that if two agents independently invent the exact same logical procedure, they will arrive at the same Semantic ID.

## 5. Security Considerations

*   **Replay Attacks**: Standard UAL packets include a timestamp (in the optional extended header) to prevent replay.
*   **Malicious Definitions**: The consensus layer requires logical validation. A definition that creates an infinite loop in the parser is automatically rejected.
