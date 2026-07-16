import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SpeedRamp(Node):
    def __init__(self):
        super().__init__("speed_ramp")
        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.timer = self.create_timer(0.5, self.send_command)
        self.speed = 0.0
        self.get_logger().info("speed ramp started: publishing to /turtle1/cmd_vel")
    def send_command(self):
        msg = Twist()
        msg.linear.x = self.speed
        msg.angular.z = 0.5
        self.publisher.publish(msg)
        self.get_logger().info(f"sending -> forward: {msg.linear.x:.1f}, turn: {msg.angular.z:.1f}")
        self.speed += 0.1
    
def main(args=None):
    rclpy.init(args=args)
    node = SpeedRamp()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()