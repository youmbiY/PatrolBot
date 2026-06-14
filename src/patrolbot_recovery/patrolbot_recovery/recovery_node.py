#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist
import time

class RecoveryNode(Node):
    STUCK_VEL_THRESHOLD = 0.01
    STUCK_TIME_THRESHOLD = 5.0
    MAX_RECOVERY_ATTEMPTS = 3

    def __init__(self):
        super().__init__('recovery_node')
        self.stuck_since = None
        self.recovery_attempts = 0
        self.is_recovering = False

        # Subscriber vitesse
        self.create_subscription(
            Twist, '/cmd_vel', self.vel_cb, 10)

        # Publisher commandes directes
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Publisher statut recovery
        self.status_pub = self.create_publisher(
            String, '/recovery/status', 10)

        # Timer monitoring toutes les secondes
        self.create_timer(1.0, self.monitor)

        self.get_logger().info('Recovery Node démarré !')

        self.delivery_state = 'IDLE'
        self.create_subscription(String, '/delivery/status', self.delivery_status_cb, 10)

    def vel_cb(self, msg):
        speed = abs(msg.linear.x) + abs(msg.angular.z)
        if speed < self.STUCK_VEL_THRESHOLD:
            if self.stuck_since is None:
                self.stuck_since = self.get_clock().now()
        else:
            if not self.is_recovering:
                self.stuck_since = None

    def monitor(self):
        if self.stuck_since is None or self.is_recovering:
            return
        if self.delivery_state in ['IDLE', 'NAVIGATING', 'RETURNING']:
            return
        elapsed = (self.get_clock().now() -
                  self.stuck_since).nanoseconds / 1e9
        if elapsed < self.STUCK_TIME_THRESHOLD:
            return
        self.get_logger().warn(
            f'BLOCAGE détecté ({elapsed:.1f}s) !')
        self.execute_recovery()

    def execute_recovery(self):
        self.is_recovering = True
        self.recovery_attempts += 1
        self.publier_status(f'RECOVERING attempt {self.recovery_attempts}')

        if self.recovery_attempts == 1:
            self.get_logger().info('Recovery 1: Backup')
            self.backup()
        elif self.recovery_attempts == 2:
            self.get_logger().info('Recovery 2: Spin')
            self.spin_360()
        elif self.recovery_attempts >= self.MAX_RECOVERY_ATTEMPTS:
            self.get_logger().error('Recovery échoué — alerte !')
            self.publier_status('RECOVERY_FAILED')

        self.is_recovering = False
        self.stuck_since = None
        if self.recovery_attempts >= self.MAX_RECOVERY_ATTEMPTS:
            self.recovery_attempts = 0

    def backup(self, distance=0.3):
        msg = Twist()
        msg.linear.x = -0.1
        duration = distance / 0.1
        end_time = time.time() + duration
        while time.time() < end_time:
            self.cmd_pub.publish(msg)
            time.sleep(0.1)
        self.stop()

    def spin_360(self):
        msg = Twist()
        msg.angular.z = 1.0
        duration = 3.14 / 0.5
        end_time = time.time() + duration
        while time.time() < end_time:
            self.cmd_pub.publish(msg)
            time.sleep(0.1)
        self.stop()

    def stop(self):
        msg = Twist()
        self.cmd_pub.publish(msg)

    def publier_status(self, status):
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

    def delivery_status_cb(self, msg):
        self.delivery_state = msg.data.replace('STATE:', '')
        if self.delivery_state == 'IDLE':
            self.stuck_since = None
            self.recovery_attempts = 0

def main(args=None):
    rclpy.init(args=args)
    executor = rclpy.executors.MultiThreadedExecutor()
    node = RecoveryNode()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
