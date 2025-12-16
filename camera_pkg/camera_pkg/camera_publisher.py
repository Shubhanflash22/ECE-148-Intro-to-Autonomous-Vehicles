#!/usr/bin/env python3
  
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

import cv2
import numpy as np

from roboflowoak import RoboflowOak


class TargetPublisher(Node):
    def __init__(self, node_name: str = "target_publisher"):
        super().__init__(node_name)

        self.angle_per_pix = 40.35 / 1080.0
        self.center_x = 384

        self.rf = None

        self.get_logger().info("We are running here")
        if RoboflowOak is None:
            self.get_logger().error(
                "roboflowoak is not installed. Running in disabled mode."
            )
        else:
            try:
                advanced_config = {
                    "nn_mode": "device"
                }

                self.rf = RoboflowOak(
                    model="car-object-detection-vw2le-5heye",
                    confidence=0.70,
                    overlap=0.5,
                    version="2",
                    api_key="IpD3gmocehhqtUawnLjh",
                    rgb=True,
                    depth=True,
                    device=None,
                    blocking=True
                )
                self.get_logger().info("RoboflowOak initialized successfully.")
            except Exception as e:
                self.get_logger().error(
                    f"Failed to initialize RoboflowOak: {e}. "
                    "Running in disabled mode."
                )
                self.rf = None

        self.publisher_ = self.create_publisher(
            Float32MultiArray, "/camera_data", 10
        )
        self.timer = self.create_timer(0.05, self.publish_target)

        self.get_logger().info(f"{node_name} Ready...")

    def publish_target(self):
        msg = Float32MultiArray()
        data = []

        if self.rf is None:
            msg.data = [float("inf"), float("inf")]
            self.publisher_.publish(msg)
            return
        result, frame, raw_frame, depth = self.rf.detect()
        predictions = result.get("predictions", [])

        if len(predictions) == 0:
            msg.data = [float("inf"), float("inf")]
            self.publisher_.publish(msg)
            self.get_logger().info("no target")
            return

        best = max(predictions, key=lambda p: p.confidence)

        x = best.x

        data.append(0.0)
        angle = (self.center_x - x) * self.angle_per_pix
        data.append(angle)

        self.get_logger().info(f"angle: {angle:.3f}")

        msg.data = data
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TargetPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()


