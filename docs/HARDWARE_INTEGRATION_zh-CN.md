# 🔌 UAL 硬件接入与集成指南

UAL (Universal Agent Language) 旨在实现“一次定义，处处运行”。无论是在强大的云服务器，还是资源受限的微控制器上，UAL 都能提供一致的语义通信能力。

本文档详细说明了不同类型硬件平台的接入方式。

---

## 📋 平台选择指南

| 硬件平台 | 典型设备 | 推荐方案 | 语言 | 依赖 |
| :--- | :--- | :--- | :--- | :--- |
| **高性能计算** | PC, Server, Mac, Cloud | **UAL Python SDK** | Python 3.8+ | `pip install ual` |
| **边缘计算** | Raspberry Pi, Jetson Nano | **UAL Python SDK** | Python 3.8+ | `pip install ual` |
| **嵌入式/MCU** | Arduino, ESP32, STM32 | **UAL Embedded** | C / C++ | `protobuf-c` |
| **机器人集群** | ROS2 Robots, AGV | **UAL Gateway** | Python/C++ | ROS2 / MQTT |

---

## 1. 高性能与边缘计算 (Python SDK)

适用于拥有完整操作系统（Linux, Windows, macOS）的设备。

### ✅ 接入步骤
1. **安装 UAL**:
   ```bash
   pip install ual
   ```
2. **编写代码**:
   ```python
   from ual import UAL

   agent = UAL("Edge_Device_01")
   
   # 发送指令
   binary_data = agent.encode("Turn on the cooling fan")
   
   # 接收指令
   def on_message(binary):
       msg = agent.decode(binary)
       if msg.nodes[0].value == "turn_on":
           print("🌀 Fan Activated!")
   ```

---

## 2. 嵌入式与单片机 (Embedded C)

适用于 Arduino, ESP32, STM32 等无操作系统或运行 RTOS 的设备。

### 🔧 前置要求
你需要安装 `protobuf-c` 编译器来生成协议代码。
- **macOS**: `brew install protobuf-c`
- **Ubuntu**: `sudo apt-get install protobuf-c-compiler`

### ✅ 接入步骤

#### 步骤 1: 生成协议代码
在你的开发机上运行：
```bash
# 假设你在项目根目录
mkdir -p generated
protoc-c --c_out=generated -I spec spec/ual.proto
```
这将生成 `ual.pb-c.h` 和 `ual.pb-c.c`。

#### 步骤 2: 准备项目文件
将以下文件复制到你的 MCU 项目目录（如 Arduino sketch 文件夹）：
- `src/ual-embedded/ual_core.h`
- `src/ual-embedded/ual_core.c`
- `generated/ual.pb-c.h`
- `generated/ual.pb-c.c`

#### 步骤 3: 编写固件代码 (Arduino 示例)
```cpp
#include "ual_core.h"
#include "ual.pb-c.h"

// 定义串口缓冲区
uint8_t buffer[256];

void setup() {
  Serial.begin(115200);
  // 初始化 UAL (如有必要)
}

void loop() {
  if (Serial.available()) {
    size_t len = Serial.readBytes(buffer, 256);
    
    // 1. 解包 UAL 消息
    Ual__Graph* graph = ual_unpack(buffer, len);
    
    if (graph) {
      // 2. 解析语义 (遍历节点)
      for (size_t i = 0; i < graph->n_nodes; i++) {
        Ual__Node* node = graph->nodes[i];
        
        // 0xA8 = Turn On, 0xED = Light
        if (node->semantic_id == 0xA8) { 
           digitalWrite(LED_BUILTIN, HIGH); 
        }
        else if (node->semantic_id == 0xA9) { // Turn Off
           digitalWrite(LED_BUILTIN, LOW);
        }
      }
      
      // 3. 释放内存
      ual_free_unpacked(graph);
    }
  }
}
```

---

## 3. 机器人与工业网关 (ROS2 / MQTT)

适用于现有的机器人生态系统。

### ✅ ROS2 接入
UAL 提供了 `ual_bridge` 节点，可将 ROS2 Topic 转换为 UAL 语义指令。

```bash
# 启动桥接节点
ros2 run ual_bridge bridge_node --ros-args -p topic:=/cmd_vel
```
当 UAL 收到 `"Move forward"` 时，桥接器会自动发布 `Twist` 消息到 `/cmd_vel`。

### ✅ MQTT 接入 (IoT)
适用于工业传感器网络。

```python
from ual.gateway import MQTTAdapter

adapter = MQTTAdapter(broker="mqtt.factory.local", topic="ual/commands")

@adapter.on_command
def handle_command(graph):
    if graph.has_action("emergency_stop"):
        hardware.halt()
```

---

## 📚 常见问题 (FAQ)

**Q: 嵌入式版本支持所有 UAL 特性吗？**
A: `ual-embedded` 目前专注于**执行 (Runtime)**。它支持解包、遍历图结构和简单的打包。复杂的语义推断（如 LLM 解析）应在云端或网关层完成，然后将编译好的二进制 UAL 发送给单片机。

**Q: 如何自定义我的硬件词汇？**
A: 使用 **Semantic Hub**。
1. 在 PC 上创建 `my_hardware.yaml`。
2. 定义你的专属 ID (如 `0x5001: ["stepper_motor"]`)。
3. 运行 `tools/hub_sync.py` 分发给所有控制端。
4. 在嵌入式代码中硬编码对应的 ID (`#define ID_STEPPER 0x5001`) 进行判断。
