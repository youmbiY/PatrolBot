#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import time
import threading

class PatrolBot(Node):
    def __init__(self):
        super().__init__('patrolbot')
        self.navigator = BasicNavigator()
        self.code_livraison = "1234"
        self.timeout = 30
        self.get_logger().info('PatrolBot est prêt')

    def initialiser_pose(self, x=0.0, y=0.0):
        """Définir la position initiale du robot sur la carte"""
        self.get_logger().info('Initialisation de la pose...')
        pose_initiale = PoseStamped()
        pose_initiale.header.frame_id = 'map'
        pose_initiale.header.stamp = self.navigator.get_clock().now().to_msg()
        pose_initiale.pose.position.x = x
        pose_initiale.pose.position.y = y
        pose_initiale.pose.orientation.w = 1.0
        self.navigator.setInitialPose(pose_initiale)
        # Attendre qu'AMCL soit prêt
        time.sleep(3)
        self.get_logger().info('Pose initiale définie !')

    def creer_pose(self, x, y):
        """Créer un objectif de position"""
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.w = 1.0
        return pose

    def aller_a(self, x, y):
        """Naviguer vers une position"""
        self.get_logger().info(f'Déplacement vers ({x}, {y})')
        goal_pose = self.creer_pose(x, y)
        self.navigator.goToPose(goal_pose)

        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()
            time.sleep(0.1)

        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('✅ Destination atteinte !')
        elif result == TaskResult.FAILED:
            self.get_logger().error('❌ Navigation échouée !')
        return result

    def livrer(self, x, y):
        """Séquence complète de livraison"""
        self.get_logger().info(f'Mission de livraison vers ({x}, {y})')

        result = self.aller_a(x, y)

        if result != TaskResult.SUCCEEDED:
            self.get_logger().error('Navigation échouée — annulation mission')
            return

        self.get_logger().info(f'Code requis (timeout: {self.timeout}s)')

        timer = threading.Timer(self.timeout, self.timeout_callback)
        timer.start()

        code = input("Code: ")
        timer.cancel()

        if code == self.code_livraison:
            self.get_logger().info('✅ Livraison confirmée !')
        else:
            self.get_logger().error('❌ Code invalide. Retour base.')
            self.retour_base()

    def timeout_callback(self):
        self.get_logger().error(f'⏰ TIMEOUT après {self.timeout}s')
        self.retour_base()

    def retour_base(self):
        self.get_logger().info('Retour à la base')
        self.aller_a(0.0, 0.0)

def main(args=None):
    rclpy.init(args=args)
    robot = PatrolBot()

    # Attendre que Nav2 soit prêt
    robot.navigator.waitUntilNav2Active()

    # Initialiser la pose du robot à (0,0) sur la carte
    robot.initialiser_pose(x=0.0, y=0.0)

    # Exécuter une livraison
    robot.livrer(x=0.5, y=0.3)

    rclpy.shutdown()

if __name__ == '__main__':
    main()
