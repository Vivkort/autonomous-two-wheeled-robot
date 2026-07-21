"""
craig2 balance controller -- LQR full-state feedback, torque architecture.

Four states, four gains, one command:

    tau = K_pitch*pitch + K_rate*pitch_rate + K_wvel*wheel_vel + K_wpos*wheel_pos

The gains were solved (not guessed) from the linearised wheeled-inverted-pendulum
model built from balancer.urdf: Mb=2.0 kg, CoM 0.20 m, Ib=0.0283, wheel r=0.05,
wheel spin inertia 0.001. Continuous-time LQR with Q=diag(0.01, 0.01, 200, 1),
R=3, then verified in a 100 Hz discrete simulation against pitch offsets to
0.30 rad, rate kicks to 3 rad/s, and velocity shocks to 1 m/s. All recovered.

Why torque and not /cmd_vel: PD on angle with velocity commands is marginally
stabilising at best -- work the ideal cart-pendulum through and the theta
coefficient stays positive for every choice of gains. It balances by accident.
This has a stability proof.

All four gains are POSITIVE and summed directly. No cascade, no target_pitch.
Wheel velocity feedback is destabilising on its own and only becomes stabilising
when paired with the position term -- that is the whole reason two gains cannot
control four states.
"""

import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist

ODOM_TOPIC = '/model/craig2/odometry'


class BalanceController(Node):
    def __init__(self):
        super().__init__('balance_controller')

        # --- LQR gains, per wheel, in the units actually measured -------------
        self.K_pitch = 4.932     # N.m per rad of lean
        self.K_rate = 0.446   # N.m per rad/s of tipping
        self.K_wvel = 1.0  # N.m per rad/s of wheel speed
        self.K_wpos = 0.02887   # N.m per rad of wheel angle
        self.K_int = 0.0015       # in __init__
        self.pos_int = 0.0
        # Traction ceiling is ~0.81 N.m/wheel at mu=1.5. The design peaks at
        # 0.24 for a 3 deg disturbance, so 0.4 leaves headroom without ever
        # commanding more force than the floor can transmit.
        self.max_torque = 0.8


        # Past this he's unrecoverable (design recovers from 0.30 rad).
        self.fall_limit = 0.9

        # Sanity guard only. Real balancing wheel speeds are well under this;
        # anything above means slip, and slipping wheel speed is not a
        # measurement of where the robot is going.
        self.wheel_vel_limit = 100.0

        self.wheel_vel = 0.0
        self.wheel_pos = 0.0
        self.odom_yaw = 0.0
        self.K_yaw = 0.5
        
        self.target_pos = 0.0
        self.cmd_vel = 0.0
        self.cmd_yaw = 0.0

        self.left_pub = self.create_publisher(
            Float64, '/model/craig2/joint/left_wheel_joint/cmd_force', 10)
        self.right_pub = self.create_publisher(
            Float64, '/model/craig2/joint/right_wheel_joint/cmd_force', 10)
        self.create_subscription(Imu, '/imu', self.balance, 10)
        self.create_subscription(Odometry, ODOM_TOPIC, self.update_odom, 10)
        self.create_subscription(Twist, '/cmd_vel', self.update_cmd, 10)

        self.get_logger().info('balance_controller up (LQR full-state)')
        self._n = 0
        self._t0 = time.monotonic()
        self._log = open('/home/viktor/balance_data.csv', 'w')
        self._log.write('t,pitch,rate,vel,pos,tau,pint,cmd,tgt,yawr,cmdyaw,odomyaw\n')
    @staticmethod
    def pitch_from(q):
        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        sinp = max(-1.0, min(1.0, sinp))
        return math.asin(sinp)

    def update_cmd(self, msg):
        self.cmd_vel = msg.linear.x 
        self.cmd_yaw = msg.angular.z

    def update_odom(self, msg):
        self.wheel_vel = msg.twist.twist.linear.x   
        self.wheel_pos = msg.pose.pose.position.x   
        q = msg.pose.pose.orientation
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.odom_yaw = math.atan2(siny, cosy)

    def balance(self, msg):
        pitch = self.pitch_from(msg.orientation)
        rate = msg.angular_velocity.y

       # setpoint slides forward at the commanded speed
        self.target_pos += self.cmd_vel * 0.0042

        MAX_LAG = 0.1
        pos_error = self.wheel_pos - self.target_pos
        if pos_error < -MAX_LAG:
            self.target_pos = self.wheel_pos + MAX_LAG
            pos_error = -MAX_LAG
        elif pos_error > MAX_LAG:
            self.target_pos = self.wheel_pos - MAX_LAG
            pos_error = MAX_LAG

        vel_error = self.wheel_vel - self.cmd_vel

        self.pos_int += pos_error * 0.0042
        self.pos_int = max(-400.0, min(400.0, self.pos_int))

        torque = (self.K_pitch * pitch
                  + self.K_rate * rate
                  + self.K_wvel * vel_error
                  + self.K_wpos * pos_error
                  + self.K_int * self.pos_int)
        
        torque = max(-self.max_torque, min(self.max_torque, torque))

        yaw_rate = msg.angular_velocity.z
        yaw_torque = self.K_yaw * (self.cmd_yaw - yaw_rate)

        left_t  = torque - yaw_torque
        right_t = torque + yaw_torque

        left_t  = max(-self.max_torque, min(self.max_torque, left_t))
        right_t = max(-self.max_torque, min(self.max_torque, right_t))

        if abs(pitch) > self.fall_limit:
            left_t = right_t = 0.0

        left, right = Float64(), Float64()
        left.data  = left_t
        right.data = right_t
        self.left_pub.publish(left)
        self.right_pub.publish(right)


        self._log.write(f'{time.monotonic():.4f},{pitch:.5f},{rate:.5f},'
                        f'{self.wheel_vel:.4f},{self.wheel_pos:.4f},{torque:.5f},'
                        f'{self.pos_int:.3f},{self.cmd_vel:.3f},{self.target_pos:.4f},'
                        f'{yaw_rate:.4f},{self.cmd_yaw:.3f},'
                        f'{self.odom_yaw:.4f}\n')
        
        self._n += 1
        now = time.monotonic()
        if now - self._t0 >= 2.0:
            self.get_logger().info(f'CONTROL RATE: {self._n / (now - self._t0):.0f} Hz')
            self._n = 0
            self._t0 = now


    def stop(self):
        self._log.close()
        try:
            zero = Float64()
            zero.data = 0.0
            self.left_pub.publish(zero)
            self.right_pub.publish(zero)
        except Exception:
            pass    # context already torn down by Ctrl+C; nothing to do


def main(args=None):
    rclpy.init(args=args)
    node = BalanceController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
