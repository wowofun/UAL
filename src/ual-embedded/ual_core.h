#ifndef UAL_CORE_H
#define UAL_CORE_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "ual.pb-c.h"

// Define a simple buffer structure
typedef struct {
    uint8_t* data;
    size_t len;
} ual_buffer_t;

// Core Functions
void ual_init_graph(Ual__Graph* graph);
Ual__Node* ual_add_node(Ual__Graph* graph, const char* id, uint32_t semantic_id, Ual__NodeType type);
void ual_add_edge(Ual__Graph* graph, const char* src_id, const char* tgt_id, Ual__RelationType rel);

// Serialization
size_t ual_get_packed_size(Ual__Graph* graph);
size_t ual_pack(Ual__Graph* graph, uint8_t* out);
Ual__Graph* ual_unpack(const uint8_t* data, size_t len);

// Helpers
void ual_free_unpacked(Ual__Graph* graph);

#endif // UAL_CORE_H
