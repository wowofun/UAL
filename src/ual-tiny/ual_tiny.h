#ifndef UAL_TINY_H
#define UAL_TINY_H

/*
 * UAL-Tiny: No-heap, minimalist decoder for Embedded Systems
 * Target: ESP32, STM32, Arduino (RAM < 20KB)
 * 
 * Usage:
 *   #define UAL_TINY_IMPLEMENTATION
 *   #include "ual_tiny.h"
 */

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

// --- Configuration Defaults ---
#ifndef UAL_MAX_NODES
#define UAL_MAX_NODES 16
#endif

#ifndef UAL_MAX_EDGES
#define UAL_MAX_EDGES 16
#endif

#ifndef UAL_ID_LEN
#define UAL_ID_LEN 16
#endif

#ifndef UAL_STR_LEN
#define UAL_STR_LEN 32
#endif

// --- Atlas Constants (Synced with atlas.py) ---
// Actions (0x0A0 range)
#define UAL_SID_MOVE        0x0A1
#define UAL_SID_SCAN        0x0A2
#define UAL_SID_GRAB        0x0A3
#define UAL_SID_RELEASE     0x0A4
#define UAL_SID_HOVER       0x0A5

// Entities (0x0E0 range)
#define UAL_SID_DRONE       0x0E1
#define UAL_SID_TARGET      0x0E2
#define UAL_SID_OBSTACLE    0x0E3
#define UAL_SID_BASE        0x0E4
#define UAL_SID_PACKAGE     0x0E5
#define UAL_SID_KITCHEN     0x0E6
#define UAL_SID_SHELF       0x0E7

// Properties (0x0B0 range)
#define UAL_SID_SPEED       0x0B1
#define UAL_SID_POSITION    0x0B2
#define UAL_SID_STATUS      0x0B3
#define UAL_SID_BATTERY     0x0B4

// Logic (0x0C0 range)
#define UAL_SID_IF          0x0C1
#define UAL_SID_THEN        0x0C2
#define UAL_SID_ELSE        0x0C3
#define UAL_SID_AND         0x0C4
#define UAL_SID_OR          0x0C5
#define UAL_SID_NOT         0x0C6

// --- Data Structures ---

typedef enum {
    UAL_NODE_UNKNOWN  = 0,
    UAL_NODE_ENTITY   = 1,
    UAL_NODE_ACTION   = 2,
    UAL_NODE_PROPERTY = 3,
    UAL_NODE_LOGIC    = 4,
    UAL_NODE_MODAL    = 5,
    UAL_NODE_VALUE    = 6,
    UAL_NODE_DATA_REF = 7
} ual_node_type_t;

typedef struct {
    char id[UAL_ID_LEN];
    uint32_t semantic_id;
    ual_node_type_t type;
    
    // Simplified value union (supports string or float)
    struct {
        bool has_str;
        char str[UAL_STR_LEN];
        bool has_num;
        double num;
    } value;
} ual_node_t;

typedef enum {
    UAL_REL_DEPENDS_ON = 0,
    UAL_REL_NEXT       = 1,
    UAL_REL_ATTRIBUTE  = 2,
    UAL_REL_ARGUMENT   = 3,
    UAL_REL_CONDITION  = 4,
    UAL_REL_CONSEQUENCE= 5,
    UAL_REL_ALTERNATIVE= 6,
    UAL_REL_TEMPORAL   = 7
} ual_relation_t;

typedef struct {
    char source_id[UAL_ID_LEN];
    char target_id[UAL_ID_LEN];
    ual_relation_t relation;
} ual_edge_t;

typedef struct {
    ual_node_t nodes[UAL_MAX_NODES];
    uint8_t node_count;
    ual_edge_t edges[UAL_MAX_EDGES];
    uint8_t edge_count;
} ual_graph_t;

// --- API Prototypes ---

/**
 * @brief Decode UAL binary payload into a Graph structure
 * @param buf Pointer to binary data
 * @param len Length of data
 * @param out_graph Pointer to pre-allocated graph struct
 * @return 0 on success, <0 on error
 */
int ual_tiny_decode(const uint8_t* buf, size_t len, ual_graph_t* out_graph);

// --- Implementation ---
#ifdef UAL_TINY_IMPLEMENTATION

// Protobuf Wire Types
#define WT_VARINT 0
#define WT_64BIT  1
#define WT_LEN    2
#define WT_32BIT  5

static uint64_t ual_read_varint(const uint8_t** ptr, const uint8_t* end) {
    uint64_t val = 0;
    int shift = 0;
    while (*ptr < end) {
        uint8_t b = **ptr;
        (*ptr)++;
        val |= (uint64_t)(b & 0x7F) << shift;
        if ((b & 0x80) == 0) return val;
        shift += 7;
        if (shift >= 64) return 0; // Error
    }
    return 0; // EOF error
}

static void ual_skip_field(const uint8_t** ptr, const uint8_t* end, int wire_type) {
    if (wire_type == WT_VARINT) {
        ual_read_varint(ptr, end);
    } else if (wire_type == WT_64BIT) {
        *ptr += 8;
    } else if (wire_type == WT_LEN) {
        uint64_t len = ual_read_varint(ptr, end);
        *ptr += len;
    } else if (wire_type == WT_32BIT) {
        *ptr += 4;
    }
}

static void ual_read_string(const uint8_t** ptr, const uint8_t* end, char* out, size_t max_len) {
    uint64_t len = ual_read_varint(ptr, end);
    if (*ptr + len > end) { *ptr = end; return; } // Overflow check
    
    size_t copy_len = (len < max_len - 1) ? len : (max_len - 1);
    memcpy(out, *ptr, copy_len);
    out[copy_len] = '\0';
    *ptr += len; // Always advance full length
}

static void ual_decode_node(const uint8_t* start, size_t len, ual_node_t* node) {
    const uint8_t* ptr = start;
    const uint8_t* end = start + len;
    
    // Defaults
    node->type = UAL_NODE_UNKNOWN;
    node->semantic_id = 0;
    node->value.has_str = false;
    node->value.has_num = false;

    while (ptr < end) {
        uint64_t tag = ual_read_varint(&ptr, end);
        int field_num = tag >> 3;
        int wire_type = tag & 7;

        switch (field_num) {
            case 1: // id (string)
                ual_read_string(&ptr, end, node->id, UAL_ID_LEN);
                break;
            case 2: // semantic_id (uint32)
                node->semantic_id = (uint32_t)ual_read_varint(&ptr, end);
                break;
            case 3: // type (enum)
                node->type = (ual_node_type_t)ual_read_varint(&ptr, end);
                break;
            case 4: // value.str_val (string)
                node->value.has_str = true;
                ual_read_string(&ptr, end, node->value.str, UAL_STR_LEN);
                break;
            case 5: // value.num_val (double)
                if (wire_type == WT_64BIT && ptr + 8 <= end) {
                    node->value.has_num = true;
                    // Assuming little-endian
                    memcpy(&node->value.num, ptr, 8);
                    ptr += 8;
                } else {
                    ual_skip_field(&ptr, end, wire_type);
                }
                break;
            default:
                ual_skip_field(&ptr, end, wire_type);
                break;
        }
    }
}

static void ual_decode_edge(const uint8_t* start, size_t len, ual_edge_t* edge) {
    const uint8_t* ptr = start;
    const uint8_t* end = start + len;
    
    while (ptr < end) {
        uint64_t tag = ual_read_varint(&ptr, end);
        int field_num = tag >> 3;
        int wire_type = tag & 7;

        switch (field_num) {
            case 1: // source_id
                ual_read_string(&ptr, end, edge->source_id, UAL_ID_LEN);
                break;
            case 2: // target_id
                ual_read_string(&ptr, end, edge->target_id, UAL_ID_LEN);
                break;
            case 3: // relation
                edge->relation = (ual_relation_t)ual_read_varint(&ptr, end);
                break;
            default:
                ual_skip_field(&ptr, end, wire_type);
                break;
        }
    }
}

static void ual_decode_graph(const uint8_t* start, size_t len, ual_graph_t* graph) {
    const uint8_t* ptr = start;
    const uint8_t* end = start + len;

    while (ptr < end) {
        uint64_t tag = ual_read_varint(&ptr, end);
        int field_num = tag >> 3;
        int wire_type = tag & 7;

        if (field_num == 1) { // nodes (repeated Node)
            uint64_t msg_len = ual_read_varint(&ptr, end);
            if (graph->node_count < UAL_MAX_NODES) {
                ual_decode_node(ptr, msg_len, &graph->nodes[graph->node_count++]);
            }
            ptr += msg_len;
        } else if (field_num == 2) { // edges (repeated Edge)
            uint64_t msg_len = ual_read_varint(&ptr, end);
            if (graph->edge_count < UAL_MAX_EDGES) {
                ual_decode_edge(ptr, msg_len, &graph->edges[graph->edge_count++]);
            }
            ptr += msg_len;
        } else {
            ual_skip_field(&ptr, end, wire_type);
        }
    }
}

int ual_tiny_decode(const uint8_t* buf, size_t len, ual_graph_t* out_graph) {
    const uint8_t* ptr = buf;
    const uint8_t* end = buf + len;
    
    // Reset graph
    out_graph->node_count = 0;
    out_graph->edge_count = 0;

    // Outer loop: Find UALMessage content (oneof payload -> Graph content = field 2)
    // BUT wait, UALMessage is the root.
    // field 2 is "oneof payload" which is Graph.
    
    while (ptr < end) {
        uint64_t tag = ual_read_varint(&ptr, end);
        int field_num = tag >> 3;
        int wire_type = tag & 7;

        if (field_num == 2 && wire_type == WT_LEN) {
            // Found Graph payload
            uint64_t graph_len = ual_read_varint(&ptr, end);
            ual_decode_graph(ptr, graph_len, out_graph);
            return 0; // Success
        } else {
            ual_skip_field(&ptr, end, wire_type);
        }
    }
    
    return -1; // Graph not found
}

#endif // UAL_TINY_IMPLEMENTATION
#endif // UAL_TINY_H
