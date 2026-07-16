#!/usr/bin/env python3
"""
velocity_listener.py

A ROS 2 node that SUBSCRIBES to velocity commands and prints them.
It's the mirror image of turtle_driver: instead of sending on a topic,
it listens on one. On the real robot, this is the pattern the motor
controller uses to RECEIVE drive commands.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class VelocityListener(Node):

    def __init__(self):
        super().__init__('velocity_listener')

        # Create a SUBSCRIPTION.
        #   - Twist: the message type we expect
        #   - '/turtle1/cmd_vel': the topic to listen on (same one the driver
        #     publishes to -- that's how they connect)
        #   - self.on_velocity: the CALLBACK function ROS calls every time a
        #     message arrives
        #   - 10: queue size, same idea as the publisher
        self.subscription = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',
            self.on_velocity,
            10)

        self.get_logger().info('velocity_listener started: listening on /turtle1/cmd_vel')

    def on_velocity(self, msg):
        """Runs automatically each time a Twist message arrives on the topic."""
        # msg is the received Twist. Pull the numbers back out of it.
        self.get_logger().info(
            f'heard -> forward: {msg.linear.x:.2f} units/s, '
            f'turn: {msg.angular.z:.2f} rad/s')


def main(args=None):
    rclpy.init(args=args)
    node = VelocityListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
