import time
import threading
import logging
from typing import Callable, Any

# Mocking external libraries to avoid dependency issues in this environment
# In production, these would be: import rclpy, import paho.mqtt.client
logger = logging.getLogger(__name__)

class UALGateway:
    """
    UAL Gateway Adapter
    Bridges UAL with ROS2 (Simulation) and MQTT.
    """
    
    def __init__(self, ual_agent, mqtt_broker="localhost", mqtt_port=1883):
        self.agent = ual_agent
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.running = False
        
        # ROS2 Mock
        self.ros_publishers = {}
        self.ros_subscribers = {}

    def start(self):
        self.running = True
        logger.info("✅ UAL Gateway Started")
        
        # Start Threads
        threading.Thread(target=self._mqtt_loop, daemon=True).start()
        threading.Thread(target=self._ros2_loop, daemon=True).start()

    def stop(self):
        self.running = False
        logger.info("🛑 UAL Gateway Stopped")

    # --- MQTT Bridge ---
    def _mqtt_loop(self):
        """Simulate MQTT listening"""
        logger.info(f"🔌 Connected to MQTT Broker at {self.mqtt_broker}:{self.mqtt_port}")
        while self.running:
            # Simulate receiving a raw JSON command from a legacy IoT device
            time.sleep(5)
            # Mock incoming message
            topic = "factory/sensor/temp"
            payload = "Alert: Overheating"
            self.on_mqtt_message(topic, payload)

    def on_mqtt_message(self, topic, payload):
        """Convert Legacy MQTT -> UAL"""
        logger.info(f"📥 MQTT Received [{topic}]: {payload}")
        
        # Transcode to UAL
        # 1. Parse intent
        ual_binary = self.agent.encode(payload, urgency=0.8)
        
        # 2. Forward to UAL Network (Mock)
        logger.info(f"➡️ Forwarded to UAL Network (Size: {len(ual_binary)} bytes)")

    # --- ROS2 Bridge ---
    def _ros2_loop(self):
        """Simulate ROS2 Node"""
        logger.info("🤖 ROS2 Node 'ual_bridge' initialized")
        while self.running:
            time.sleep(3)
            # Simulate ROS2 /cmd_vel to UAL Action
            # Linear: 1.0, Angular: 0.5
            self.on_ros_command({"linear": 1.0, "angular": 0.5})

    def on_ros_command(self, twist_msg):
        """Convert ROS2 Twist -> UAL Graph"""
        # Mapping: Twist -> Move Action
        # Create Graph manually or via encode
        # Let's use encode for simplicity
        cmd_str = f"Move speed {twist_msg['linear']} turn {twist_msg['angular']}"
        
        # UAL Encode
        # Note: Ideally we map Twist fields directly to Node values for efficiency
        # But NLP interface is the universal fallback
        binary = self.agent.encode(cmd_str)
        logger.info(f"🔄 ROS2 Twist -> UAL Command ({len(binary)} bytes)")

    # --- UAL -> External ---
    def send_to_ros(self, topic: str, ual_graph):
        """Convert UAL Graph -> ROS2 Message"""
        # Logic to extract 'Move' action and publish Twist
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Mock UAL Agent
    from ual import UAL
    agent = UAL("Gateway_01")
    
    gateway = UALGateway(agent)
    gateway.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gateway.stop()
