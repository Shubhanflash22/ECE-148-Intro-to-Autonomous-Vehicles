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

# ROI settings
ROI = (200, 200, 200, 200)  # x, y, w, h

# Detection parameters
WINDOW = 30                # number of frames to keep for FFT
BRIGHT_MIN_PIXELS = 5      # minimum red pixels to consider a blink
DIFF_THRESHOLD = 15.0      # frame-to-frame mean difference (red channel)
FFT_FREQ_LOW = 2.0         # min blink frequency in Hz
FFT_FREQ_HIGH = 10.0       # max blink frequency in Hz
FPS = 30                   # camera FPS


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
        self.prev_red_mask = None
        self.get_logger().info('Red blink detector started.')

     # Red color HSV thresholds
        self.lower_red1 = np.array([0, 120, 70])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([170, 120, 70])
        self.upper_red2 = np.array([180, 255, 255])

    def check_lock(self):
        return os.path.exists(LOCK_FILE)
    def stop_and_exit(self):
        msg = Bool()
        msg.data = True
        self.pub.publish(msg)
        self.get_logger().info("Red blink detected → Sent signal!")

    # ❌ Do NOT delete monitor.lock
    # if os.path.exists(LOCK_FILE):
    #     os.remove(LOCK_FILE)

    # Keep running—just keep logging
        self.get_logger().info("Blinking detected (continuing to monitor).")

    def callback(self, msg):
        if not self.check_lock():
            self.get_logger().info("monitor.lock missing → exiting.")
            rclpy.shutdown()
            return

        # Convert ROS image to OpenCV BGR
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        x, y, w, h = ROI
        roi = frame[y:y+h, x:x+w]

        # Convert ROI to HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Create red mask
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)

        # Count red pixels
        BRIGHT_THRESHOLD = 100
        red_mask = cv2.bitwise_and(red_mask, red_mask)
        red_pixels = np.sum(red_mask > BRIGHT_THRESHOLD)
        #red_pixels = np.sum(red_mask > 0)
        bright_spot_ok = red_pixels >= BRIGHT_MIN_PIXELS

        # Frame difference check
        frame_diff_ok = False
        if self.prev_red_mask is not None:
            diff = np.abs(red_mask.astype(float) - self.prev_red_mask.astype(float))
            mean_diff = np.mean(diff)
            if mean_diff > DIFF_THRESHOLD:
                frame_diff_ok = True
        self.prev_red_mask = red_mask

        # FFT check on mean red intensity
        mean_red = float(np.mean(red_mask))
        self.brightness_hist.append(mean_red)
        if len(self.brightness_hist) > WINDOW:
            self.brightness_hist.pop(0)

        fft_ok = False
        if len(self.brightness_hist) == WINDOW:
            y = np.array(self.brightness_hist) - np.mean(self.brightness_hist)
            fft = np.fft.rfft(y)
            freqs = np.fft.rfftfreq(WINDOW, d=1.0/FPS)
            fft_amp = np.abs(fft)
            blink_freq_indices = np.where((freqs >= FFT_FREQ_LOW) & (freqs <= FFT_FREQ_HIGH))[0]
            if np.any(fft_amp[blink_freq_indices] > (0.5 * np.max(fft_amp))):
                fft_ok = True

        # Trigger only if all three conditions satisfied
        if bright_spot_ok and frame_diff_ok and fft_ok:
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
