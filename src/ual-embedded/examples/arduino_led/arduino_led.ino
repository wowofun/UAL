/*
 * UAL Embedded Example: LED Controller
 * 
 * Hardware: ESP32 or Arduino
 * Logic: Receives UAL Binary Packet over Serial -> Decodes -> Controls LED
 * 
 * Dependencies:
 * - protobuf-c library
 * 
 * Setup:
 * 1. Generate ual.pb-c.c/h using protoc-c
 * 2. Copy ual.pb-c.c, ual.pb-c.h, ual_core.c, ual_core.h to this folder
 */

#ifdef ARDUINO
  #include <Arduino.h>
#else
  #include <stdio.h>
  #define Serial_println(x) printf("%s\n", x)
#endif

#include "ual_core.h"

// ESP32 Onboard LED is usually GPIO 2
#define LED_PIN 2

void process_graph(Ual__Graph* graph);

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  
  // Blink to indicate startup
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("UAL Node Ready. Waiting for Graph Packet...");
}

void loop() {
  if (Serial.available()) {
    // Read packet
    // In real world, use a delimiter or length prefix.
    // Here we just wait for a burst of data.
    delay(100); // Wait for full message
    
    uint8_t buffer[512];
    size_t len = 0;
    while (Serial.available() && len < sizeof(buffer)) {
      buffer[len++] = Serial.read();
    }
    
    Serial.print("Received bytes: ");
    Serial.println(len);
    
    // Decode
    Ual__Graph* graph = ual_unpack(buffer, len);
    if (graph) {
      Serial.println("Decoded UAL Graph!");
      process_graph(graph);
      ual_free_unpacked(graph);
    } else {
      Serial.println("Error: Failed to decode protobuf.");
    }
  }
}

void process_graph(Ual__Graph* graph) {
  bool turn_on = false;
  bool turn_off = false;
  
  for (size_t i = 0; i < graph->n_nodes; i++) {
    Ual__Node* node = graph->nodes[i];
    
    // Check Semantic IDs (defined in atlas.yaml)
    // 0xA8 = Turn On
    // 0xA9 = Turn Off
    if (node->semantic_id == 0xA8) {
      turn_on = true;
    }
    if (node->semantic_id == 0xA9) {
      turn_off = true;
    }
  }
  
  if (turn_on) {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("Action: LED ON");
  } else if (turn_off) {
    digitalWrite(LED_PIN, LOW);
    Serial.println("Action: LED OFF");
  } else {
    Serial.println("No relevant action found.");
  }
}
