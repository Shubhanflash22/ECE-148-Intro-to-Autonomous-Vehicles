#!/usr/bin/env python

import rclpy
import math
from rclpy.node import Node
# import the LaserScan module from sensor_msgs interface
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist
# import Quality of Service library, to set the correct profile and reliability to read sensor data.
from rclpy.qos import ReliabilityPolicy, QoSProfile
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import Bool

class dist_publisher(Node):
    def __init__(self, node_name="dist_publisher"):
        self.keep_dist = 0.5 #distance in m to keep from lead car
        
        # PID tuning
        self.p_a = 1.75 #P term for turning
        self.p_d = 1.5 #P term for throttle
        self.d_a = 1.2 #D term for turning
        self.d_d = 0.2 #D term for throttle
        
        #for d term
        self.last_a_err = 0
        self.last_d_err = 0
        
        
        self._node_name = node_name
        self.data = []
        self.tar_ang = 0.0
        self.tar_ind = round(math.pi/2/0.014005)
        self.ang_inc = 0.2
        self.tar_found = False
        self.blink_detected =False
        super().__init__(self._node_name)

        #subscriber to get lidar data
        self.subscriber_lidar = self.create_subscription(
            LaserScan,
            '/scan',
            self.laserscan_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE))
        
        #subscriber to get camera data
        self.subscriber_cam = self.create_subscription(
            Float32MultiArray,
            '/camera_data',
            self.target_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE))
       
        self.subscriber_blink = self.create_subscription(
            Bool,
            '/blink_detected',
            self.on_trigger,
            10
        )

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.05  # seconds
        self.timer = self.create_timer(timer_period, self.publish_dist)

        self.get_logger().info(self._node_name +" Ready...")

    # callback for lidar subscriber
    def laserscan_callback(self, msg):
        # Save the data for the node to use later
        self.data = msg.ranges
        self.ang_inc = msg.angle_increment
        self.ang_min = msg.angle_min

    # callback for camera target subscriber
    def target_callback(self,msg):
        if msg.data[1] == float('inf'):
            self.tar_found = False
        else:
            self.tar_found = True

            # 1. Get Camera Angle (in radians)
            # Assuming msg.data[1] is in degrees relative to camera center
            cam_angle = math.radians(msg.data[1])

            # 2. Convert to LiDAR Frame
            # (Only keep +math.pi/2 if your Camera is physically rotated 90 deg
            # relative to the Lidar's 0 angle. Otherwise, remove it.)
            # specific_offset = math.pi/2
            target_angle_in_lidar_frame = cam_angle
            self.tar_ang = cam_angle

            # 3. Calculate Index Safely
            # Formula: index = (desired_angle - start_angle) / increment
            if hasattr(self, 'ang_min') and hasattr(self, 'ang_inc'):
                index = (target_angle_in_lidar_frame - self.ang_min) / self.ang_inc
                self.tar_ind = int(round(index))

                # 4. Clamp Index to prevent crashes
                self.tar_ind = max(0, min(self.tar_ind, len(self.data) - 1))

    def on_trigger(self, msg: Bool):
        """Callback for /blink_detected subscription."""
        if msg.data:
            self.get_logger().info("Blink detected: TRUE")
            self.blink_detected = True
        else:
            self.get_logger().info("Blink detected: FALSE")
            self.blink_detected = True

    def publish_dist(self):
        """Calculates and publishes velocity commands based on target distance."""
        cmd_msg = Twist()

        # If blinking sign not detected
        if not self.blink_detected:
            cmd_msg.linear.x = 0.0
            cmd_msg.angular.z = 0.0
        else:
            # --- 1 case 1. Check if we have a usable distance reading at tar_ind ---
            has_valid_dist = (
                self.data
                and self.tar_ind is not None
                and 0 <= self.tar_ind < len(self.data)
                and self.data[self.tar_ind] != float('inf')
            )

            # --- 1 case2. No target or bad LiDAR → go forward, unless already close ---
            if not has_valid_dist or not self.tar_found:
                self.get_logger().warn('No valid target or LiDAR data. Drive forward (unless too close).')

                forward_speed = 0.4  # default: move forward

                if has_valid_dist:
                    current_dist = self.data[self.tar_ind]
                    # If the distance is close, stop instead of moving forward
                    if current_dist <= self.keep_dist:
                        forward_speed = 0.0

                cmd_msg.linear.x = forward_speed
                cmd_msg.angular.z = 0.0
                self.publisher_.publish(cmd_msg)
                return

            # 2. Get State
            current_dist = self.data[self.tar_ind]
            dist_error = current_dist - self.keep_dist

            # 3. Safety Check: Stop if too close
            if dist_error <= 0.0:
                self.get_logger().info(f"Target too close: {current_dist:.3f}m. Stopping.")
                self.publisher_.publish(cmd_msg)
                return

            # 4. Compute Control Signals
            linear_vel = self._compute_linear_control(dist_error)
            angular_vel = self._compute_angular_control(current_dist)

            # 5. Apply Reverse Logic
            # If reversing, invert steering so we don't turn into the obstacle
            if linear_vel < 0:
                angular_vel = -angular_vel

            # 6. Publish
            cmd_msg.linear.x = linear_vel
            cmd_msg.angular.z = angular_vel

        # 7. Publish
        self.publisher_.publish(cmd_msg)

        # Logging (Optional: Log less frequently to avoid console spam)
        self.get_logger().info(f"Dist: {current_dist:.2f}m | Angle Err: {math.degrees(self.last_a_err):.1f}°")


    def _compute_linear_control(self, error):
        """PD Controller for Linear Velocity (Distance)."""
        # PD Calculation
        derivative = error - self.last_d_err
        control_signal = (self.p_d * error) + (self.d_d * derivative)

        # Update State
        self.last_d_err = error

        # Clamp max speed to 1.0 (Safety)
        return min(0.4, control_signal)

    def _compute_angular_control(self, current_dist):
        """PD Controller for Angular Velocity (Steering)."""
        # Calculate Error (Targeting math.pi based on your snippet)
        angle_error = 0.1 - self.tar_ang
        if current_dist >=1.5:
            angle_error = angle_error * math.sqrt(current_dist)

        # PD Calculation
        derivative = angle_error - self.last_a_err
        control_signal = (self.p_a * angle_error) + (self.d_a * derivative)

        # Update State
        self.last_a_err = angle_error

        return control_signal
        
        
def main(args=None):
    rclpy.init(args=args)
    node = dist_publisher()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        # Spin the executor
        executor.spin()
    finally:
        # Cleanup
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

