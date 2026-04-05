import numpy as np
import time
from stable_baselines3 import DQN, DDPG, TD3
from stable_baselines3.common.noise import NormalActionNoise
from env import RobotEnv

# ========================
# Evaluation Function
# ========================
def evaluate_model(model, env, episodes=3):
    rewards = []
    collisions = 0
    success = 0
    times = []

    for ep in range(episodes):
        state, _ = env.reset()
        done = False
        truncated = False
        ep_reward = 0
        start_time = time.time()

        while not done and not truncated:
            if isinstance(model, DQN):
                action, _states = model.predict(state, deterministic=True)
            else:
                action, _ = model.predict(state, deterministic=True)

            state, reward, done, truncated, _ = env.step(action)
            ep_reward += reward

            if reward < 0:
                collisions += 1

        end_time = time.time()
        times.append(end_time - start_time)
        rewards.append(ep_reward)
        if ep_reward > 0:
            success += 1

    avg_reward = int(np.mean(rewards))
    success_rate = int((success / episodes) * 100)
    total_collisions = collisions
    avg_time = int(np.mean(times))

    return avg_reward, success_rate, total_collisions, avg_time

# ========================
# Train and Compare Models
# ========================

# --- DQN ---
env_dqn = RobotEnv(continuous=False, algo_name="DQN", print_every=5)
model_dqn = DQN("MlpPolicy", env_dqn, verbose=0)
print("Training DQN...")
model_dqn.learn(total_timesteps=20000)
model_dqn.save("robot_dqn")

# --- DDPG ---
env_ddpg = RobotEnv(continuous=True, algo_name="DDPG", print_every=5)
n_actions = env_ddpg.action_space.shape[0]
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=5.0 * np.ones(n_actions))
model_ddpg = DDPG("MlpPolicy", env_ddpg, action_noise=action_noise, verbose=0)
print("Training DDPG...")
model_ddpg.learn(total_timesteps=20000)
model_ddpg.save("robot_ddpg")

# --- TD3 ---
env_td3 = RobotEnv(continuous=True, algo_name="TD3", print_every=5)
n_actions = env_td3.action_space.shape[0]
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=5.0 * np.ones(n_actions))
model_td3 = TD3("MlpPolicy", env_td3, action_noise=action_noise, verbose=0)
print("Training TD3...")
model_td3.learn(total_timesteps=20000)
model_td3.save("robot_td3")

# --- Evaluate All ---
results = {}
results['DQN'] = evaluate_model(model_dqn, env_dqn)
results['DDPG'] = evaluate_model(model_ddpg, env_ddpg)
results['TD3'] = evaluate_model(model_td3, env_td3)

# --- Print Table ---
print("\nAlgorithm Comparison Table")
print(f"{'Algorithm':<6} {'Avg Reward':<12} {'Success Rate':<14} {'Collisions':<12} {'Time to Goal':<12}")
for algo, stats in results.items():
    avg_r, success, coll, t_goal = stats
    print(f"{algo:<6} {avg_r:<12} {str(success)+'%':<14} {coll:<12} {str(t_goal)+' sec':<12}")
