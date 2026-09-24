#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class KinematicModel(Node):

    def __init__(self):
        super().__init__('kinematic_model')

        # Robot state
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        # Commanded velocities
        self.v = 0.0
        self.omega = 0.0

        # Subscriber
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Publisher
        self.odom_pub = self.create_publisher(
            Odometry,
            '/kinematic_odom',
            10
        )

        # Run the kinematic model at 50 Hz
        self.timer = self.create_timer(
            0.01,
            self.update
        )

        self.get_logger().info('Kinematic model started')


    def cmd_vel_callback(self, msg):

        self.v = msg.linear.x
        self.omega = msg.angular.z


    def update(self):

        dt = 0.01

        # Differential-drive kinematic model
        x_dot = self.v * math.cos(self.theta)
        y_dot = self.v * math.sin(self.theta)
        theta_dot = self.omega

        # Euler integration
        self.x += x_dot * dt
        self.y += y_dot * dt
        self.theta += theta_dot * dt

        # Create odometry message
        odom = Odometry()

        odom.header.stamp = self.get_clock().now().to_msg()

        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'

        # Position
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.49

        # Convert yaw -> quaternion
        odom.pose.pose.orientation.x = 0.0
        odom.pose.pose.orientation.y = 0.0
        odom.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2.0)

        # Velocity
        odom.twist.twist.linear.x = self.v
        odom.twist.twist.angular.z = self.omega

        # Publish
        self.odom_pub.publish(odom)


def main(args=None):

    rclpy.init(args=args)

    node = KinematicModel()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()