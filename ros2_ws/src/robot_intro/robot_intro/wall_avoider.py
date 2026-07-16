import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class WallAvoider(Node):
    def __init__(self):
        super().__init__('wall_avoider')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscriber = self.create_subscription(Pose, '/turtle1/pose', self.update_pose, 10)
        self.pose = None
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.avoid_wall)
    def update_pose(self, msg):
        self.pose = msg
    def avoid_wall(self):
        if self.pose is None:
            return
        if self.pose.x < 1.5 or self.pose.x > 9.5 or self.pose.y < 1.5 or self.pose.y > 9.5:
            msg = Twist()
            msg.linear.x = 1.5
            msg.angular.z = 0.9
            self.publisher.publish(msg)
        else:
            msg = Twist()
            msg.linear.x = 2.0
            msg.angular.z = 0.0
            self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = WallAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()