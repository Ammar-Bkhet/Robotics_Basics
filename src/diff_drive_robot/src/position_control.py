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

        # Target position
        self.declare_parameter('x_d', 2.0)
        self.declare_parameter('y_d', 2.0)

        # Velocities 
        self.v = 0
        self.omega = 0

    

        # Odom Publisher
        self.odom_pub = self.create_publisher(
            Odometry,
            '/kinematic_odom',
            10
        )

        # Cmd velocity Publisher
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )


        # Run the kinematic model at 50 Hz
        self.timer = self.create_timer(
            0.02,
            self.update
        )

        self.get_logger().info('Kinematic model started')


  


    def update(self):

        dt = 0.02

        self.x_d = self.get_parameter('x_d').value
        self.y_d = self.get_parameter('y_d').value

        

        # instant position to target
        dx = self.x_d - self.x 
        dy = self.y_d - self.y
        self.theta_d = math.atan2(dy,dx) 
        angle_error = math.atan2(
             math.sin(self.theta_d - self.theta),
             math.cos(self.theta_d - self.theta)
            )

    


        # Calculating velocities 
        k_v = 0.2
        k_omega = 1.5

        distance = math.sqrt((dx ** 2) + (dy ** 2))
        self.v = distance * k_v 
    

        self.omega = angle_error * k_omega


        if distance < 0.01:
            self.v = 0.0
            self.omega = 0.0




        # Create cmd vel message
        velocity = Twist() 

        velocity.linear.x = self.v
        velocity.angular.z = self.omega

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

        # Update positions 
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt
        self.theta += self.omega * dt

        # Publish
        self.odom_pub.publish(odom)
        self.cmd_vel_pub.publish(velocity)




def main(args=None):

    rclpy.init(args=args)

    node = KinematicModel()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()