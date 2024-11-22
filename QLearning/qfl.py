import random
import time
from collections import defaultdict


def q_learn(model, time_limit):
    # Hyperparameters
    # learning_rate = 0.25
    discount_factor = .99
    epsilon = 0.25 #(.1 to .25)

    # Q-table: Dictionary for grid cells and actions
    Q = defaultdict(lambda: {action: 0.0 for action in range(model.offensive_playbook_size())})
    visit_counts = defaultdict(int)
    learning_rates = defaultdict(lambda: 0.25)  # Per-bin learning rates
    

    def get_bin(state):
        yards_to_score, downs_left, yards_to_first_down, time_left = state

        progress_per_time = yards_to_score / time_left 
        progress_per_play = downs_left / yards_to_first_down
        x, y = None, None

        if progress_per_time < 2.5: #2
            x = 2
        elif progress_per_time >= 5.0: #3.6
            x = 0
        else:
            x = 1

        if progress_per_play < 0.25: #.39
            y = 0
        elif progress_per_play >= .5: #.5
            y = 2
        else:
            y = 1

        visit_counts[(x,y)] += 1
        return (x, y)

    def update_learning_rate(cell):
        # Decay the learning rate based on the number of visits
        learning_rates[cell] *= .999

    def eplison_choice(cell, actions):
        if random.random() < epsilon:
            return random.randint(0, actions - 1)
        else:
            return max(Q[cell], key=Q[cell].get)  # Action with the highest Q-value
            
    # Q-Learning loop
    start_time = time.time()
    while time.time() - start_time < time_limit:
        state = model.initial_position()
        while not model.game_over(state):
            
            # Map state to bin
            cell = get_bin(state)

            # Choose an action
            action = eplison_choice(cell, model.offensive_playbook_size())
            
            # Observe the result
            next_state, (yards_gained, time_elapsed, turnover) = model.result(state, action)

            reward = 0
            max_next_q = 0
            if model.game_over(next_state):
                #Calculate reward
                reward = 1 if model.win(next_state) else -1
            else:
                #update Q
                next_cell = get_bin(next_state)
                max_next_q = max(Q[next_cell].values()) 
            lr = learning_rates[cell]
            Q[cell][action] +=  lr * (reward + discount_factor * max_next_q - Q[cell][action])

            #update Decay
            update_learning_rate(cell)

            # Move to the next state
            state = next_state

    # print(Q)

    def policy_function(state):
        cell = get_bin(state)
        return max(Q[cell], key=Q[cell].get, default=random.randint(0, model.offensive_playbook_size() - 1)) 
    # print(max(visit_counts.values()) / min(visit_counts.values()))
    return policy_function


















