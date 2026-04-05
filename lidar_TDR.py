import rclpy
import os
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from stable_baselines3 import TD3
import numpy as np

class SmartMover(Node):
  

    def __init__(self):
        super().__init__('smart_mover')

        # 🔍 DEBUG: where ROS is running from
        print("Current working dir:", os.getcwd())

        # ROS publishers/subscribers
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10
        )


        # Timer for smooth control
        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz
        self.lidar_state = [1.0] * 30
        # State variables
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.current_turn = 0.0
        self.target_turn = 0.0
        self.model = TD3.load("robot_td3")
        self.state = np.zeros(31)
        self.mindist = 1.0

    def listener_callback(self, msg):
    
        raw = msg.ranges[:360]
        processed = []
        for v in raw:
            if v == float('inf') or v != v:
                processed.append(1.0)
            else:
                processed.append(min(float(v) / 3.5, 1.0))

        if len(processed) == 0:
            return

    # 🔥 TAKE 30 RAYS (same as training)
        import numpy as np
        indices = np.linspace(0, 359, 30).astype(int)
        lidar_30 = np.array([processed[i] for i in indices])

    # 🔥 GOAL ANGLE (for now 0)
        goal_angle = 0.0

    # 🔥 FINAL STATE FOR AI
        self.state = np.append(lidar_30, goal_angle)
    
    # Smooth acceleration
    def control_loop(self):
        cmd = Twist()

    # 🔥 AI ACTION
        action, _ = self.model.predict(self.state, deterministic=True)
        turn = float(action[0])

    # 🔥 CLAMP (IMPORTANT)
        self.target_turn = max(-1.0, min(turn, 1.0))

    # Speed
        self.target_speed = 0.4

    # Smooth motion (keep your existing smoothing)
        accel = 0.05
        turn_accel = 0.1

        if self.current_speed < self.target_speed:
            self.current_speed += accel
        elif self.current_speed > self.target_speed:
            self.current_speed -= accel

        if self.current_turn < self.target_turn:
            self.current_turn += turn_accel

    # Clamp final
        self.current_speed = max(0.0, min(self.current_speed, 1.0))
        self.current_turn = max(-2.0, min(self.current_turn, 2.0))

        cmd.linear.x = self.current_speed
        cmd.angular.z = self.current_turn

        self.publisher.publish(cmd)

def main():
    rclpy.init()
    node = SmartMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
