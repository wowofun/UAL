import time
import threading
import logging
from typing import Callable, Any

# --- Import Simulation ---
# In a real environment, these would be standard imports
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    from geometry_msgs.msg import Twist
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    # Mock classes for environment without ROS2
    class Node:
        def __init__(self, name): self.name = name
        def create_subscription(self, *args): pass
        def create_publisher(self, *args): return type('MockPub', (), {'publish': lambda x: None})()
        def get_logger(self): return logging.getLogger(self.name)
    class Twist:
        linear = type('Vec3', (), {'x': 0.0, 'y': 0.0, 'z': 0.0})()
        angular = type('Vec3', (), {'x': 0.0, 'y': 0.0, 'z': 0.0})()

logger = logging.getLogger(__name__)

class UALRosNode(Node):
    """
    Official ROS2 Node for UAL.
    Intercepts standard ROS messages and converts them to UAL protocol.
    """
    def __init__(self, ual_agent):
        super().__init__('ual_bridge_node')
        self.agent = ual_agent
        
        # 1. Subscriber: Intercept Legacy Commands (String)
        # e.g., /chatter or /robot_cmd_text
        self.subscription = self.create_subscription(
            String,
            'legacy_text_cmd',
            self.listener_callback,
            10
        )
        
        # 2. Publisher: Output UAL Binary Stream
        # In a real scenario, this might go to a serial port or a custom topic
        self.ual_pub = self.create_publisher(String, 'ual_stream', 10)
        
        # 3. Publisher: Control Robot (Twist)
        # We also listen to UAL commands and drive the robot
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        self.get_logger().info("✅ UAL ROS2 Node Initialized. Listening on 'legacy_text_cmd'...")

    def listener_callback(self, msg):
        """
        Callback for legacy text messages.
        Intercepts string -> Encodes to UAL -> Broadcasts
        """
        text_command = msg.data
        self.get_logger().info(f"👂 Intercepted Legacy Command: '{text_command}'")
        
        # 1. Convert to UAL Binary (The "Magic")
        start_time = time.time()
        ual_binary = self.agent.encode(text_command)
        compression_time = (time.time() - start_time) * 1000
        
        # 2. Log Performance
        original_size = len(text_command.encode('utf-8'))
        ual_size = len(ual_binary)
        ratio = (1 - ual_size/original_size) * 100 if original_size > 0 else 0
        
        self.get_logger().info(
            f"⚡ Transcoded to UAL: {original_size}B -> {ual_size}B "
            f"(Saved {ratio:.1f}%) in {compression_time:.2f}ms"
        )
        
        # 3. Publish UAL Stream (Simulated as Hex String for ROS std_msgs)
        out_msg = String()
        out_msg.data = ual_binary.hex()
        self.ual_pub.publish(out_msg)
        
        # 4. Execute Locally (Optional: Decode back to drive robot)
        # This demonstrates "Thinking in UAL, Acting in ROS"
        decoded = self.agent.decode(ual_binary)
        self.execute_ual_action(decoded)

    def execute_ual_action(self, decoded_msg):
        """
        Translates UAL semantic logic into physical ROS2 Twist commands.
        """
        intent = decoded_msg.get('natural_language', '').lower()
        twist = Twist()
        
        if 'move' in intent:
            twist.linear.x = 1.0
            self.get_logger().info("🤖 Action: Moving Forward")
        elif 'stop' in intent:
            twist.linear.x = 0.0
            self.get_logger().info("🤖 Action: Stopping")
        elif 'turn' in intent:
            twist.angular.z = 0.5
            self.get_logger().info("🤖 Action: Turning")
            
        self.cmd_vel_pub.publish(twist)

class UALGateway:
    """
    Wrapper to run the ROS2 node.
    """
    def __init__(self, ual_agent):
        self.agent = ual_agent
        self.ros_node = None
        self.executor_thread = None

    def start(self):
        if not ROS_AVAILABLE:
            logger.warning("⚠️ ROS2 (rclpy) not found. Running in MOCK mode.")
        else:
            rclpy.init()
            
        self.ros_node = UALRosNode(self.agent)
        
        # Spin ROS node in a separate thread
        if ROS_AVAILABLE:
            self.executor_thread = threading.Thread(target=rclpy.spin, args=(self.ros_node,), daemon=True)
            self.executor_thread.start()
        else:
            # Mock loop
            threading.Thread(target=self._mock_ros_loop, daemon=True).start()

    def stop(self):
        if ROS_AVAILABLE:
            self.ros_node.destroy_node()
            rclpy.shutdown()
        logger.info("🛑 Gateway Stopped")

    def _mock_ros_loop(self):
        """Simulates incoming messages for testing without ROS installed"""
        logger.info("🔮 Starting Mock ROS Loop...")
        time.sleep(1)
        # Simulate an incoming message object
        msg = type('Msg', (), {'data': 'Robot move forward speed 5'})()
        self.ros_node.listener_callback(msg)
        
        time.sleep(2)
        msg.data = "Emergency stop now"
        self.ros_node.listener_callback(msg)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from ual import UAL
    
    agent = UAL("ROS_Bot_01")
    gateway = UALGateway(agent)
    gateway.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gateway.stop()
