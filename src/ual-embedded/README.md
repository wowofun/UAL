# UAL Embedded Core (C/C++)

这是一个轻量级的 UAL 核心实现，专为嵌入式设备（如 Arduino, ESP32, STM32）设计。它不依赖 Python，仅依赖 standard C 和 `protobuf-c`。

## 目录结构
- `ual_core.h/c`: UAL 图结构的核心操作（节点/边管理、序列化）。
- `generated/`: 存放由 `protoc-c` 生成的代码。
- `examples/`: 示例项目。

## 快速开始

### 1. 生成 Protobuf-C 代码
你需要安装 `protobuf-c-compiler`。
```bash
# macOS
brew install protobuf-c

# 生成代码
mkdir -p generated
protoc-c --c_out=generated -I../../spec ../../spec/ual.proto
```

### 2. 编译核心库
使用 CMake 编译静态库：
```bash
mkdir build && cd build
cmake ..
make
```

### 3. 运行 Arduino 示例
请参考 `examples/arduino_led/README.md` (如有) 或直接打开 `examples/arduino_led/arduino_led.ino`。
你需要将 `ual_core.h/c` 和 `generated/ual.pb-c.h/c` 复制到 Arduino 项目文件夹中。
