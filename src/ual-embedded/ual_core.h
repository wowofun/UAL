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

// Parameter Parsing Helpers
Ual__Node* ual_find_node_by_semantic_id(Ual__Graph* graph, uint32_t semantic_id);
Ual__Node* ual_find_node_by_id(Ual__Graph* graph, const char* id);
Ual__Node* ual_find_target_node(Ual__Graph* graph, const char* src_id, Ual__RelationType rel);

int ual_get_node_int(Ual__Node* node, int default_val);
float ual_get_node_float(Ual__Node* node, float default_val);
const char* ual_get_node_str(Ual__Node* node, const char* default_val);

// Advanced Helpers
int ual_get_action_param_int(Ual__Graph* graph, const char* action_id, uint32_t param_semantic_id, int default_val);


#endif // UAL_CORE_H
