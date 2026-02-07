#include "ual_core.h"
#include <stdlib.h>
#include <string.h>

// Simple strdup implementation for embedded systems that might miss it
static char* ual_strdup(const char* s) {
    if (!s) return NULL;
    size_t len = strlen(s) + 1;
    char* new_s = (char*)malloc(len);
    if (new_s) {
        memcpy(new_s, s, len);
    }
    return new_s;
}

void ual_init_graph(Ual__Graph* graph) {
    ual__graph__init(graph);
}

Ual__Node* ual_add_node(Ual__Graph* graph, const char* id, uint32_t semantic_id, Ual__NodeType type) {
    Ual__Node** new_nodes = (Ual__Node**)realloc(graph->nodes, sizeof(Ual__Node*) * (graph->n_nodes + 1));
    if (!new_nodes) return NULL;
    graph->nodes = new_nodes;

    Ual__Node* node = (Ual__Node*)malloc(sizeof(Ual__Node));
    if (!node) return NULL;
    ual__node__init(node);
    
    node->id = ual_strdup(id);
    node->semantic_id = semantic_id;
    node->type = type;
    
    graph->nodes[graph->n_nodes] = node;
    graph->n_nodes++;
    
    return node;
}

void ual_add_edge(Ual__Graph* graph, const char* src_id, const char* tgt_id, Ual__RelationType rel) {
    Ual__Edge** new_edges = (Ual__Edge**)realloc(graph->edges, sizeof(Ual__Edge*) * (graph->n_edges + 1));
    if (!new_edges) return;
    graph->edges = new_edges;

    Ual__Edge* edge = (Ual__Edge*)malloc(sizeof(Ual__Edge));
    if (!edge) return;
    ual__edge__init(edge);
    
    edge->source_id = ual_strdup(src_id);
    edge->target_id = ual_strdup(tgt_id);
    edge->relation = rel;
    
    graph->edges[graph->n_edges] = edge;
    graph->n_edges++;
}

size_t ual_get_packed_size(Ual__Graph* graph) {
    return ual__graph__get_packed_size(graph);
}

size_t ual_pack(Ual__Graph* graph, uint8_t* out) {
    return ual__graph__pack(graph, out);
}

Ual__Graph* ual_unpack(const uint8_t* data, size_t len) {
    return ual__graph__unpack(NULL, len, data);
}

void ual_free_unpacked(Ual__Graph* graph) {
    ual__graph__free_unpacked(graph, NULL);
}

Ual__Node* ual_find_node_by_semantic_id(Ual__Graph* graph, uint32_t semantic_id) {
    if (!graph || !graph->nodes) return NULL;
    for (size_t i = 0; i < graph->n_nodes; i++) {
        if (graph->nodes[i]->semantic_id == semantic_id) {
            return graph->nodes[i];
        }
    }
    return NULL;
}

Ual__Node* ual_find_node_by_id(Ual__Graph* graph, const char* id) {
    if (!graph || !graph->nodes || !id) return NULL;
    for (size_t i = 0; i < graph->n_nodes; i++) {
        if (graph->nodes[i]->id && strcmp(graph->nodes[i]->id, id) == 0) {
            return graph->nodes[i];
        }
    }
    return NULL;
}

Ual__Node* ual_find_target_node(Ual__Graph* graph, const char* src_id, Ual__RelationType rel) {
    if (!graph || !graph->edges || !src_id) return NULL;
    for (size_t i = 0; i < graph->n_edges; i++) {
        if (strcmp(graph->edges[i]->source_id, src_id) == 0 && graph->edges[i]->relation == rel) {
             return ual_find_node_by_id(graph, graph->edges[i]->target_id);
        }
    }
    return NULL;
}

int ual_get_node_int(Ual__Node* node, int default_val) {
    if (!node) return default_val;
    if (node->value_case == UAL__NODE__VALUE_NUM_VAL) {
        return (int)node->num_val;
    }
    return default_val;
}

float ual_get_node_float(Ual__Node* node, float default_val) {
    if (!node) return default_val;
    if (node->value_case == UAL__NODE__VALUE_NUM_VAL) {
        return (float)node->num_val;
    }
    return default_val;
}

const char* ual_get_node_str(Ual__Node* node, const char* default_val) {
    if (!node) return default_val;
    if (node->value_case == UAL__NODE__VALUE_STR_VAL) {
        return node->str_val;
    }
    return default_val;
}

int ual_get_action_param_int(Ual__Graph* graph, const char* action_id, uint32_t param_semantic_id, int default_val) {
    if (!graph || !action_id) return default_val;
    
    // Find edges from action
    for (size_t i = 0; i < graph->n_edges; i++) {
        if (strcmp(graph->edges[i]->source_id, action_id) == 0) {
             Ual__Node* target = ual_find_node_by_id(graph, graph->edges[i]->target_id);
             if (!target) continue;

             // Case 1: Target IS the parameter (matches semantic ID) and has value
             if (target->semantic_id == param_semantic_id) {
                 // Check if value is on this node
                 if (target->value_case == UAL__NODE__VALUE_NUM_VAL) {
                     return (int)target->num_val;
                 }
                 
                 // Case 2: Target is Unit/Key, Value is attached via Attribute
                 Ual__Node* value_node = ual_find_target_node(graph, target->id, UAL__RELATION_TYPE__ATTRIBUTE);
                 if (value_node) {
                     return ual_get_node_int(value_node, default_val);
                 }
             }
        }
    }
    return default_val;
}
