#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

class CarControl(Node):
    def __init__(self):
        super().__init__('car_control_example')
        self.create_subscription(
            Bool,
            '/blink_detected',
            self.on_trigger,
            10
        )
        self.get_logger().info("Car control node ready — waiting for blink...")

    def on_trigger(self, msg):
        if msg.data:
            self.get_logger().info("Received TRIGGER → Car would react here.")
            # TODO: Add GPIO / motor control logic here
            # Example: toggle GPIO pin, send command over CAN, etc.

def main():
    rclpy.init()
    node = CarControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
