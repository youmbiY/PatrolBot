#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped
import threading
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Variables globales partagées
robot_x = 0.0
robot_y = 0.0
robot_state = 'IDLE'
connected_clients = []

app = FastAPI(title='PatrolBot API', version='1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'],
                   allow_methods=['*'], allow_headers=['*'])

class MissionRequest(BaseModel):
    destination_x: float
    destination_y: float
    delivery_code: str

class CodeRequest(BaseModel):
    code: str

@app.get('/api/status')
async def get_status():
    return {
        'robot_x': robot_x,
        'robot_y': robot_y,
        'state': robot_state
    }

@app.post('/api/mission')
async def create_mission(req: MissionRequest):
    ros_node.publish_mission(req.destination_x, req.destination_y, req.delivery_code)
    return {'status': 'mission_accepted'}

@app.post('/api/code')
async def submit_code(req: CodeRequest):
    ros_node.publish_code(req.code)
    return {'status': 'code_submitted'}

@app.websocket('/ws/tracking')
async def tracking_ws(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    try:
        while True:
            data = {
                'x': robot_x,
                'y': robot_y,
                'state': robot_state
            }
            await ws.send_json(data)
            await asyncio.sleep(0.5)
    except Exception:
        connected_clients.remove(ws)

class APIServerNode(Node):
    def __init__(self):
        super().__init__('api_server')
        global ros_node
        ros_node = self

        # Publisher missions et codes
        self.mission_pub = self.create_publisher(String, '/delivery/new_mission', 10)
        self.code_pub = self.create_publisher(String, '/delivery/code_submitted', 10)

        # Subscriber statut et position
        self.create_subscription(String, '/delivery/status', self.status_cb, 10)
        self.create_subscription(
            PoseWithCovarianceStamped, '/amcl_pose', self.pose_cb, 10)

        self.get_logger().info('API Server démarré sur http://localhost:5000')
        self.get_logger().info('Swagger UI: http://localhost:5000/docs')

    def status_cb(self, msg):
        global robot_state
        robot_state = msg.data.replace('STATE:', '')

    def pose_cb(self, msg):
        global robot_x, robot_y
        robot_x = round(msg.pose.pose.position.x, 3)
        robot_y = round(msg.pose.pose.position.y, 3)
        self.get_logger().info(f'Position mise à jour: ({robot_x}, {robot_y})')

    def publish_mission(self, x, y, code):
        msg = String()
        msg.data = f'{x},{y},{code}'
        self.mission_pub.publish(msg)
        self.get_logger().info(f'Mission publiée: ({x}, {y}) code:{code}')

    def publish_code(self, code):
        msg = String()
        msg.data = code
        self.code_pub.publish(msg)
        self.get_logger().info(f'Code publié: {code}')

def ros_thread_func():
    rclpy.init()
    node = APIServerNode()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()

def main(args=None):
    t = threading.Thread(target=ros_thread_func, daemon=True)
    t.start()
    import time
    time.sleep(2)
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level='warning')

if __name__ == '__main__':
    main()
