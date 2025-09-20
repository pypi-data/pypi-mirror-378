setup = """
import random
import numpy as np
num_agents = 1
state_size = 1000
action_size = 10000
from q_learning_list import MultiAgentQLearningLists
from q_learning_numpy import MultiAgentQLearningNumpy
ql = MultiAgentQLearningLists(num_agents, state_size, action_size)
ql.q_table = [random.random() for _ in range(state_size * action_size)]
qn = MultiAgentQLearningNumpy(num_agents, state_size, action_size)
qn.q_table = np.array(ql.q_table).reshape(state_size, action_size)
action_masks = [[random.randint(0, 1) for _ in range(action_size)] for _ in range(num_agents)]
states = [random.randint(0, state_size - 1) for _ in range(num_agents)]
actions = [random.randint(0, action_size - 1) for _ in range(num_agents)]
rewards = [random.random() for _ in range(num_agents)]
next_states = [random.randint(0, state_size - 1) for _ in range(num_agents)]
np_action_masks = np.array(action_masks)
np_states = np.array(states)
np_actions = np.array(actions)
np_rewards = np.array(rewards)
np_next_states = np.array(next_states)
"""

# num_agents = 1000
# state_size = 2
# action_size = 2
# from q_learning_list import MultiAgentQLearningLists

# ql = MultiAgentQLearningLists(num_agents, state_size, action_size)
# import random

# action_masks = [[random.randint(0, 1) for _ in range(action_size)] for _ in range(num_agents)]
# states = [random.randint(0, state_size - 1) for _ in range(num_agents)]
# actions = [random.randint(0, action_size - 1) for _ in range(num_agents)]
# rewards = [random.random() for _ in range(num_agents)]
# next_states = [random.randint(0, state_size - 1) for _ in range(num_agents)]

num_iter = 1000

# Test QLearningLists.learn function
