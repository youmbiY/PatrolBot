#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
import numpy as np

class AIPlanner(Node):
    def __init__(self):
        super().__init__('ai_planner')
        # Poids configurables
        self.declare_parameter('w_distance', 0.25)
        self.declare_parameter('w_time', 0.20)
        self.declare_parameter('w_obstacles', 0.35)
        self.declare_parameter('w_risk', 0.15)
        self.declare_parameter('w_energy', 0.05)

        self.obstacle_density = [0.0] * 36

        # Subscriber densité obstacles
        self.create_subscription(
            Float32MultiArray,
            '/obstacle_density',
            self.density_cb, 10)

        # Publisher score
        self.score_pub = self.create_publisher(
            String, '/ai_planner/score', 10)

        # Timer pour publier le score toutes les secondes
        self.create_timer(1.0, self.publier_score)

        self.get_logger().info('AI Planner démarré !')

    def density_cb(self, msg):
        self.obstacle_density = list(msg.data)

    def compute_score(self, x, y):
        """Calculer le score d'un chemin vers (x, y)"""
        # Critère D : distance
        distance = np.sqrt(x**2 + y**2)

        # Critère T : temps estimé
        temps = distance / 0.22

        # Critère O : densité obstacles moyenne
        obstacle_cost = float(np.mean(self.obstacle_density)) if self.obstacle_density else 0.0

        # Critère R : risque zone (simplifié)
        risk = 0.0

        # Critère E : coût énergétique (simplifié)
        energy = distance * 0.1

        # Récupérer les poids
        w1 = self.get_parameter('w_distance').value
        w2 = self.get_parameter('w_time').value
        w3 = self.get_parameter('w_obstacles').value
        w4 = self.get_parameter('w_risk').value
        w5 = self.get_parameter('w_energy').value

        # Score final normalisé
        score = (w1 * distance/10.0 +
                 w2 * temps/45.0 +
                 w3 * obstacle_cost +
                 w4 * risk +
                 w5 * energy)

        return score

    def choisir_meilleur_chemin(self, destinations):
        """Choisir la meilleure destination parmi plusieurs"""
        meilleur_score = float('inf')
        meilleure_dest = None

        for dest in destinations:
            score = self.compute_score(dest[0], dest[1])
            self.get_logger().info(
                f'Destination ({dest[0]}, {dest[1]}) → Score: {score:.4f}')
            if score < meilleur_score:
                meilleur_score = score
                meilleure_dest = dest

        self.get_logger().info(
            f'Meilleure destination: {meilleure_dest} (score: {meilleur_score:.4f})')
        return meilleure_dest

    def publier_score(self):
        """Comparer plusieurs destinations et publier la meilleure"""
        destinations = [
            (0.5, 0.3),
            (1.0, 0.5),
            (-0.5, 0.8),
            (1.5, -0.5)
        ]
        meilleure = self.choisir_meilleur_chemin(destinations)
        score = self.compute_score(meilleure[0], meilleure[1])
        msg = String()
        msg.data = f'Meilleure destination: {meilleure} score: {score:.4f}'
        self.score_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(AIPlanner())
    rclpy.shutdown()
