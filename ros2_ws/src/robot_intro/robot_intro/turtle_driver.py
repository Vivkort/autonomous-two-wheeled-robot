#!/usr/bin/env python3
"""
turtle_driver.py

A ROS 2 node that PUBLISHES velocity commands to make a turtle drive in a circle.
This is the same pattern that will one day drive your real rover's wheels --
only the topic name changes (/turtle1/cmd_vel here, /cmd_vel on the robot).
"""

# rclpy = "ROS Client Library for PYthon". It's how python talks to ROS 2.
import rclpy
# Node is the base class every ROS 2 node inherits from.
from rclpy.node import Node
# Twist is the standard MESSAGE TYPE for velocity: a linear part (straight-line
# speed) and an angular part (turning speed). It lives in the geometry_msgs package.
from geometry_msgs.msg import Twist


class TurtleDriver(Node):
    """Our node is a class that inherits everything a ROS 2 Node can do."""

    def __init__(self):
        # Tell the parent Node class our node's name. This name shows up in
        # `ros2 node list`.
        super().__init__('turtle_driver')

        # Create a PUBLISHER.
        #   - Twist: the message type we'll send
        #   - '/turtle1/cmd_vel': the TOPIC (the named channel) we publish to
        #   - 10: the "queue size" -- how many messages to buffer if the
        #     receiver is briefly slow. 10 is a fine default.
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Create a TIMER that calls self.send_command() every 0.5 seconds.
        # ROS 2 nodes are event-driven; a timer is how you do something
        # repeatedly without writing your own while-loop.
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.send_command)

        # get_logger().info(...) prints a nicely formatted, timestamped message.
        # Prefer this over print() in ROS 2.
        self.get_logger().info('turtle_driver started: publishing to /turtle1/cmd_vel')

    def send_command(self):
        """Called by the timer. Builds a Twist message and publishes it."""
        msg = Twist()          # start with an all-zeros velocity command
        msg.linear.x = 1.0     # move forward at 1.0 units/second
        msg.angular.z = 0.5    # AND rotate at 0.5 radians/second -> a circle

        # Send the message out on the topic. Anyone subscribed receives it.
        self.publisher_.publish(msg)

        # Log what we sent so we can watch it in the terminal.
        self.get_logger().info(
            f'sending -> forward: {msg.linear.x:.1f}, turn: {msg.angular.z:.1f}')


def main(args=None):
    """Standard ROS 2 python entry point."""
    rclpy.init(args=args)          # start up ROS 2 communications
    node = TurtleDriver()          # create our node
    try:
        rclpy.spin(node)           # keep the node alive, firing its timer/callbacks
    except KeyboardInterrupt:
        pass                       # Ctrl+C exits cleanly instead of crashing
    finally:
        node.destroy_node()        # free the node's resources
        rclpy.shutdown()           # shut ROS 2 down


if __name__ == '__main__':
    main()
