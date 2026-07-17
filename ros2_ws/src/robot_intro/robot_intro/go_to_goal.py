import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
from geometry_msgs.msg import Point

class GoToGoal(Node):
    def __init__(self):
        super().__init__('go_to_goal')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscriber = self.create_subscription(Pose, '/turtle1/pose', self.update_pose, 10)
        self.subscriber_goal = self.create_subscription(Point, '/goal', self.update_goal, 10)
        self.pose = None
        self.goal = None   
        self.timer = self.create_timer(0.1, self.go_to_goal_loop)
    def update_pose(self, msg):
            self.pose = msg
    def update_goal(self, msg):
            self.goal = msg
    def go_to_goal_loop(self):
        if self.pose is None or self.goal is None:
            return 
        dx = self.goal.x - self.pose.x
        dy = self.goal.y - self.pose.y
        Ka = 4.0
        Kl = 1.0
        distance = math.hypot(dx, dy)
        msg = Twist()
        if distance < 0.2:
            pass
        else:
            desired = math.atan2(dy, dx)
            heading_error = math.atan2(math.sin(desired - self.pose.theta), math.cos(desired - self.pose.theta))
            msg.angular.z = Ka * heading_error
            msg.linear.x = min(Kl * distance, 2.0)
        self.publisher.publish(msg)
def main(args=None):
    rclpy.init(args=args)
    node = GoToGoal()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()

    