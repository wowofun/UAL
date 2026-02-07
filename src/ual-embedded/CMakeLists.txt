cmake_minimum_required(VERSION 3.10)
project(ual-embedded C)

# Find Protobuf-C
find_path(PROTOBUF_C_INCLUDE_DIR google/protobuf-c/protobuf-c.h)
find_library(PROTOBUF_C_LIBRARY protobuf-c)

if(NOT PROTOBUF_C_INCLUDE_DIR OR NOT PROTOBUF_C_LIBRARY)
    message(WARNING "Protobuf-C not found. Please install it.")
endif()

# Source files
set(SOURCES
    ual_core.c
    ual.pb-c.c
)

add_library(ual-embedded STATIC ${SOURCES})

target_include_directories(ual-embedded PUBLIC 
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${PROTOBUF_C_INCLUDE_DIR}
)

target_link_libraries(ual-embedded ${PROTOBUF_C_LIBRARY})
