#!/usr/bin/env python3
"""my_first_node.py -- we build this up together, one step at a time."""

import rclpy                          # the Python <-> ROS 2 bridge
from rclpy.node import Node           # base class every node inherits from
from geometry_msgs.msg import Twist   # NEW: the velocity message (WHAT we send)


class MyFirstNode(Node):
    def __init__(self):
        super().__init__('my_first_node')
        self.get_logger().info('Hello! my_first_node is alive.')

        self.count = 0

        # NEW: a PUBLISHER -- our node's mouth. It lets us send Twist messages
        # out on the topic '/turtle1/cmd_vel', which the turtle is listening to.
        # (Twist type, topic name, queue size of 10.)
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # timer = WHEN: call self.tick every 0.5 seconds
        self.timer = self.create_timer(0.5, self.tick)

    def tick(self):
        self.count += 1

        # WHAT: build a velocity command
        msg = Twist()
        msg.linear.x = 1.0      # drive forward
        msg.angular.z = 0.5     # and turn -> a circle

        # HOW: send it out. The turtle receives it and moves.
        self.publisher_.publish(msg)

        self.get_logger().info(
            f'tick #{self.count}: sending forward={msg.linear.x}, turn={msg.angular.z}')


def main(args=None):
    rclpy.init(args=args)
    node = MyFirstNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
