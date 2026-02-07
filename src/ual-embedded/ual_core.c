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
