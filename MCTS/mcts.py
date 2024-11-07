import time
import math
import random

class Node:
    def __init__(self, state, action=None):
        self.state = state
        self.parent = None
        self.children = []
        self.n = 0
        self.r = 0
        self.actor = state.actor()
        self.action = action
        self.expanded = False

def UCB(r, n, T, actor):
    exploration = math.sqrt(2 * math.log(T) / n)
    if actor == 0:  
        return (r / n) + exploration
    else:           
        return (r / n) - exploration

def traverse(node):
    while node.expanded:
        unvisited_children = []
        for child in node.children:
            if child.n == 0:
                unvisited_children.append(child)
        if unvisited_children:
            return random.choice(unvisited_children)

        T = node.n
        if node.actor == 0:
            ucb_child = max(
                node.children,
                key=lambda child: UCB(child.r, child.n, T, node.actor))
            
        else: 
            ucb_child = min(
                node.children,
                key=lambda child: UCB(child.r, child.n, T, node.actor))
        node = ucb_child
    return node

def expand(node):
    if not node.state.is_terminal() and not node.expanded and node.n != 0:
        actions = node.state.get_actions()
        for action in actions:
            new_state = node.state.successor(action)
            new_node = Node(new_state, action)
            new_node.parent = node
            node.children.append(new_node)
        node.expanded = True
        return random.choice(node.children)
    return node

def simulate(state):
    while not state.is_terminal():
        action = random.choice(state.get_actions())
        state = state.successor(action)
    return state.payoff()

def update(node, r):
    if node:
        node.r += r
        node.n += 1
        update(node.parent, r)

def mcts_policy(time_limit):
    def search(state):
        root = Node(state)
        start_time = time.time()
        while(time.time() - start_time < time_limit):
            #traverse
            leaf = traverse(root)
            #expand
            expanded_node = expand(leaf)
            #simulate
            reward = simulate(expanded_node.state)
            #update
            update(expanded_node, reward)
        if root.actor == 0:
            return max(root.children, key=lambda c: c.r / c.n).action
        else:
            # print("# of actions", len(root.state.get_actions()))
            # print("# of childrens", len(root.children))
            # print("# of root", root.n)
            # for c in root.children:
            #     print("here", c.n)
            return min(root.children, key=lambda c: c.r / c.n).action
    return search

