import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

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
        
        x = self.pose.x
        y = self.pose.y
        nearest = min(x, 11.0 - x, y, 11.0 - y)

        safe = 3.0
        Kp = 1.2
        Kv = 0.8
        
        msg = Twist()
        if nearest < safe:
            desired = math.atan2(5.5 - y, 5.5 - x)
            heading_error = math.atan2(math.sin(desired - self.pose.theta), math.cos(desired - self.pose.theta))
            error = safe - nearest
            msg.angular.z = Kp *heading_error
            msg.linear.x = max(0.5, 2.0 - Kv* error)
    
        else:
            msg.angular.z = 0.0
            msg.linear.x = 2.0
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = WallAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()