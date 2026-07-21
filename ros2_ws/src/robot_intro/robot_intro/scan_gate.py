import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry


class ScanGate(Node):
    def __init__(self):
        super().__init__('scan_gate')
        # arcsin(0.50 lidar height / 4.0 max range) - past this the
        # beam hits floor instead of walls. Change either number, change this.
        self.limit = 0.1257          # rad = 7.2 deg
        self.pitch = 0.0             # MUST initialise - scans can beat odom
        self.was_open = True

        self.pub = self.create_publisher(LaserScan, '/scan_gated', 10)
        self.create_subscription(Odometry, '/odom', self.update_odom, 10)
        self.create_subscription(LaserScan, '/scan', self.gate_scan, 10)
    @staticmethod
    def pitch_from(q):
        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        sinp = max(-1.0, min(1.0, sinp))
        return math.asin(sinp)
    
    def update_odom(self, msg):
        self.pitch = self.pitch_from(msg.pose.pose.orientation)

    def gate_scan(self, msg):
        open = abs(self.pitch) < self.limit
        if open:
            self.pub.publish(msg)
        if open != self.was_open:
            state = 'RESUMED' if open else 'PAUSED'
            self.get_logger().info(f'mapping {state} at {self.pitch*57.2958:.1f} deg')
            self.was_open = open
    

def main(args=None):
    rclpy.init(args=args)
    node = ScanGate()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

