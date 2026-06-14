#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from enum import Enum, auto
import hashlib
import threading
import time

class DeliveryState(Enum):
    IDLE = auto()
    NAVIGATING = auto()
    ARRIVED = auto()
    WAITING_CODE = auto()
    VERIFYING = auto()
    DELIVERING = auto()
    RETURNING = auto()
    ERROR = auto()

class DeliveryManager(Node):
    CODE_TIMEOUT = 120.0

    def __init__(self):
        super().__init__('delivery_manager')
        self.state = DeliveryState.IDLE
        self.navigator = BasicNavigator()
        self.code_livraison = "1234"
        self.code_timer = None

        # Publishers
        self.status_pub = self.create_publisher(String, '/delivery/status', 10)

        # Subscribers
        self.create_subscription(String, '/delivery/new_mission', self.mission_cb, 10)
        self.create_subscription(String, '/delivery/code_submitted', self.code_cb, 10)

        self.get_logger().info('Delivery Manager démarré !')
        self.publier_status()

    def transition(self, new_state, reason=''):
        self.get_logger().info(f'FSM: {self.state.name} → {new_state.name} [{reason}]')
        self.state = new_state
        self.publier_status()

    def publier_status(self):
        msg = String()
        msg.data = f'STATE:{self.state.name}'
        self.status_pub.publish(msg)

    def verify_code(self, submitted, expected):
        h1 = hashlib.sha256(submitted.encode()).hexdigest()
        h2 = hashlib.sha256(expected.encode()).hexdigest()
        return h1 == h2

    def creer_pose(self, x, y):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.w = 1.0
        return pose

    def mission_cb(self, msg):
        if self.state != DeliveryState.IDLE:
            self.get_logger().warn('Mission en cours — ignorée')
            return
        try:
            parts = msg.data.split(',')
            x = float(parts[0])
            y = float(parts[1])
            code = parts[2]
            self.code_livraison = code
            self.get_logger().info(f'Nouvelle mission → ({x}, {y}) code:{code}')
            threading.Thread(target=self.executer_mission, args=(x, y)).start()
        except Exception as e:
            self.get_logger().error(f'Erreur mission: {e}')
            self.transition(DeliveryState.ERROR, str(e))

    def code_cb(self, msg):
        if self.state == DeliveryState.WAITING_CODE:
            self.get_logger().info(f'Code reçu: {msg.data}')
            self.transition(DeliveryState.VERIFYING, 'code reçu')
            if self.code_timer:
                self.code_timer.cancel()
            if self.verify_code(msg.data, self.code_livraison):
                self.transition(DeliveryState.DELIVERING, 'code correct')
                self.get_logger().info('✅ Livraison confirmée !')
                time.sleep(2)
                self.transition(DeliveryState.RETURNING, 'livraison terminée')
                threading.Thread(target=self.retour_base).start()
            else:
                self.transition(DeliveryState.RETURNING, 'code incorrect')
                threading.Thread(target=self.retour_base).start()

    def executer_mission(self, x, y):
        self.transition(DeliveryState.NAVIGATING, f'vers ({x},{y})')
        goal = self.creer_pose(x, y)
        self.navigator.goToPose(goal)
        while not self.navigator.isTaskComplete():
            time.sleep(0.1)
        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.transition(DeliveryState.ARRIVED, 'destination atteinte')
            self.transition(DeliveryState.WAITING_CODE, 'attente code')
            self.code_timer = threading.Timer(
                self.CODE_TIMEOUT, self.timeout_callback)
            self.code_timer.start()
        else:
            self.transition(DeliveryState.ERROR, 'navigation échouée')

    def timeout_callback(self):
        self.get_logger().error(f'⏰ TIMEOUT {self.CODE_TIMEOUT}s')
        self.transition(DeliveryState.RETURNING, 'timeout')
        self.retour_base()

    def retour_base(self):
        goal = self.creer_pose(0.0, 0.0)
        self.navigator.goToPose(goal)
        while not self.navigator.isTaskComplete():
            time.sleep(0.1)
        self.transition(DeliveryState.IDLE, 'retour base terminé')

def main(args=None):
    rclpy.init(args=args)
    node = DeliveryManager()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
