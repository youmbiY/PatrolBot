#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray
import numpy as np

class ObstacleDetectorNode(Node):
    def __init__(self):
        super().__init__('obstacle_detector')
        self.declare_parameter('num_sectors', 36)
        self.declare_parameter('danger_distance', 1.0)
        self.num_sectors = self.get_parameter('num_sectors').value
        self.danger_dist = self.get_parameter('danger_distance').value
        self.sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.pub = self.create_publisher(Float32MultiArray, '/obstacle_density', 10)
        self.get_logger().info('ObstacleDetector démarré !')

    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)
        ranges = np.where(np.isinf(ranges), msg.range_max, ranges)
        ranges = np.where(np.isnan(ranges), msg.range_max, ranges)
        sector_size = len(ranges) // self.num_sectors
        densities = []
        for i in range(self.num_sectors):
            sector = ranges[i*sector_size:(i+1)*sector_size]
            density = float(np.sum(sector < self.danger_dist) / len(sector))
            densities.append(density)
        out = Float32MultiArray()
        out.data = densities
        self.pub.publish(out)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(ObstacleDetectorNode())
    rclpy.shutdown()
