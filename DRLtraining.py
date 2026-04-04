from stable_baselines3 import DQN
from env import RobotEnv

print("Creating environment...")
env = RobotEnv()

print("Creating model...")
model = DQN("MlpPolicy", env, verbose=1)

print("Starting training...")
model.learn(total_timesteps=50000)

print("Training finished!")
model.save("robot_dqn")
