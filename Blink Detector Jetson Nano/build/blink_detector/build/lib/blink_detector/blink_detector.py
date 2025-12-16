#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool
from cv_bridge import CvBridge
import cv2
import numpy as np
import os
import sys
import time

LOCK_FILE = '/home/projects/monitor.lock'
ROI = (200, 200, 200, 200)  # x, y, w, h
WINDOW = 20
THRESHOLD = 25.0
FPS = 30

class BlinkDetector(Node):
    def __init__(self):
        super().__init__('blink_detector')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.callback,
            10
        )
        self.pub = self.create_publisher(Bool, '/blink_detected', 10)
        self.brightness_hist = []
        self.get_logger().info('Blink detector started.')

    def check_lock(self):
        return os.path.exists(LOCK_FILE)

    def stop_and_exit(self):
        msg = Bool()
        msg.data = True
        self.pub.publish(msg)
        self.get_logger().info("Blink detected → Sent signal!")
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            self.get_logger().info("Removed monitor.lock (system halted).")
        time.sleep(0.5)
        self.get_logger().info("Exiting detector.")
        rclpy.shutdown()
        sys.exit(0)

    def callback(self, msg):
        if not self.check_lock():
            self.get_logger().info("monitor.lock missing → exiting.")
            rclpy.shutdown()
            return

        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        x, y, w, h = ROI
        roi = frame[y:y+h, x:x+w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))

        self.brightness_hist.append(brightness)
        if len(self.brightness_hist) > WINDOW:
            self.brightness_hist.pop(0)

        if len(self.brightness_hist) == WINDOW:
            amp = max(self.brightness_hist) - min(self.brightness_hist)
            if amp > THRESHOLD:
                self.stop_and_exit()

def main():
    rclpy.init()
    node = BlinkDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
