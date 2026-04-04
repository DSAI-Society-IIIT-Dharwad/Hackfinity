import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

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

        # Timer for smooth control
        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz

        # State variables
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.current_turn = 0.0
        self.target_turn = 0.0

        self.mindist = 1.0

    def listener_callback(self, msg):
        count = 0
        raw = msg.ranges[:360]
        processed = []

        for v in raw:
            if v == float('inf') or v != v:
                processed.append(1.0)
                count += 1
            else:
                processed.append(min(float(v) / 3.5, 1.0))
                count += 1

        if len(processed) == 0:
            return
        print(count)
        # Debug
        self.get_logger().info(f"LiDAR sample: {processed[:10]}")

        min0 = min(processed[0:10])
        min1 = min(processed[-10:])
        self.mindist = min(min0, min1)

    def control_loop(self):
        cmd = Twist()

        # Decision logic
        if self.mindist < 0.35:
            self.target_speed = 0.0
            self.target_turn = 0.75   # turn left
        else:
            self.target_speed = 0.4
            self.target_turn = 0.0

        # Smooth acceleration
        accel = 0.05
        turn_accel = 0.1

        # Linear smoothing
        if self.current_speed < self.target_speed:
            self.current_speed += accel
        elif self.current_speed > self.target_speed:
            self.current_speed -= accel

        # Angular smoothing
        if self.current_turn < self.target_turn:
            self.current_turn += turn_accel
        elif self.current_turn > self.target_turn:
            self.current_turn -= turn_accel

        # Clamp values
        self.current_speed = max(0.0, min(self.current_speed, 1.0))
        self.current_turn = max(-2.0, min(self.current_turn, 2.0))

        cmd.linear.x = self.current_speed
        cmd.angular.z = self.current_turn

        self.publisher.publish(cmd)

        self.get_logger().info(
            f"Speed: {self.current_speed:.2f}, Turn: {self.current_turn:.2f}, Dist: {self.mindist:.2f}"
        )


def main():
    rclpy.init()
    node = SmartMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
