import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np


class SmartMover(Node):

    def __init__(self):
        super().__init__('smart_mover')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10
        )

        self.timer = self.create_timer(0.1, self.control_loop)

        # Full LiDAR state
        self.lidar = np.ones(360)
        self.prev_angle = 0.0
        self.lock_steps = 0
        self.locked_turn = 0.0
        # Motion
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.current_turn = 0.0
        self.target_turn = 0.0

        # Heading (goal is 0 rad)
        self.heading = 0.0

    def get_action(self):

    # 🔥 If locked → continue same motion
        if self.lock_steps > 0:
            self.lock_steps -= 1
            return 0.5, self.locked_turn

        angles = np.linspace(-np.pi, np.pi, 360)

        goal_alignment = np.cos(angles - self.heading)
        obstacle_penalty = 1.0 - self.lidar

        score = (
            1.0 * self.lidar +
            0.4 * goal_alignment -
            1.2 * obstacle_penalty
        )

        best_index = np.argmax(score)
        best_angle = angles[best_index]

    # 🔥 Convert to stable turn
        turn = np.clip(best_angle, -1.0, 1.0)

    # 🔥 Speed
        speed = 0.5 * (1 - abs(turn))

    # 🔥 COMMIT to this decision
        self.locked_turn = turn
        self.lock_steps = 5   # commit for 5 cycles (~0.5 sec)

        return float(speed), float(turn)
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

        self.lidar = np.array(processed)

    def control_loop(self):
        cmd = Twist()

        self.target_speed, self.target_turn = self.get_action()

        accel = 0.05
        turn_accel = 0.1

        # Smooth speed
        if self.current_speed < self.target_speed:
            self.current_speed += accel
        elif self.current_speed > self.target_speed:
            self.current_speed -= accel

        # Smooth turn
        if self.target_turn == 0.0:
            self.current_turn = 0.0
        else:
            if self.current_turn < self.target_turn:
                self.current_turn += turn_accel
            elif self.current_turn > self.target_turn:
                self.current_turn -= turn_accel

        # 🔥 Update heading (memory of orientation)
        self.heading += self.current_turn * 0.1

        # Normalize heading
        if self.heading > np.pi:
            self.heading -= 2 * np.pi
        elif self.heading < -np.pi:
            self.heading += 2 * np.pi

        # Clamp motion
        self.current_speed = max(0.0, min(self.current_speed, 1.0))
        self.current_turn = max(-2.0, min(self.current_turn, 2.0))

        cmd.linear.x = self.current_speed
        cmd.angular.z = self.current_turn

        self.publisher.publish(cmd)

        self.get_logger().info(
            f"Speed: {self.current_speed:.2f}, Turn: {self.current_turn:.2f}, Heading: {self.heading:.2f}"
        )


def main():
    rclpy.init()
    node = SmartMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
