import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
import math

class BalanceController(Node):
    def __init__(self):
        super().__init__('balance_controller')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscriber = self.create_subscription(Imu, '/imu', self.balance, 10)
        self.Kp = 15
        self.Ki = 0.0
        self.Kd = 2.0
        self.integral = 0.0
        self.dt = 0.01
    def balance(self, msg):
        q = msg.orientation
        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        sinp = max(-1.0, min(1.0, sinp))
        pitch = math.asin(sinp)
        error = pitch
        rate = msg.angular_velocity.y
        self.integral += error * self.dt

        output = self.Kp * error + self.Ki * self.integral + self.Kd * rate

        cmd = Twist()
        cmd.linear.x = output
        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = BalanceController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()