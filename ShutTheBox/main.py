import itertools
import sys
import random
class ShutTheBox:
    def __init__(self, player, action, position, p1_score=None, roll=None):
        self.player = player  #'--one' or '--two'
        self.action = action  #'--expect' or '--move'
        self.position = position  #list of open tiles
        self.p1_score = p1_score
        self.roll = roll
        self.memo = {}
        self.prob = [0, 0, 1/36, 1/18, 1/12, 1/9, 5/36, 1/6, 5/36, 1/9, 1/12, 1/18, 1/36] #prob of getting each sum (index i) for 2 dice
        self.p2_prob = {
             0: 0.000000, #Don't think the 0 case is possible/not valid input for --two --expect tiles 0
             1: 0.113912,
             2: 0.146717,
             3: 0.179369,
             4: 0.212770,
             5: 0.249410,
             6: 0.285286,
             7: 0.328292,
             8: 0.381212,
             9: 0.438357,
            10: 0.493920,
            11: 0.544614,
            12: 0.591782,
            13: 0.636685,
            14: 0.678696,
            15: 0.717814,
            16: 0.754159,
            17: 0.788031,
            18: 0.818650,
            19: 0.845389,
            20: 0.870293,
            21: 0.892103,
            22: 0.909997,
            23: 0.925558,
            24: 0.938774,
            25: 0.951303,
            26: 0.960898,
            27: 0.967612,
            28: 0.973788,
            29: 0.979165,
            30: 0.983581,
            31: 0.987102,
            32: 0.990796,
            33: 0.992990,
            34: 0.994065,
            35: 0.995244,
            36: 0.996271,
            37: 0.997053,
            38: 0.998114,
            39: 0.998778,
            40: 0.999100,
            41: 0.999228,
            42: 0.999228,
            43: 0.999614,
            44: 1.000000,
            45: 1.000000
        }

    def get_possible_actions(self, open_tiles, roll):
        #generate all subsets of open_tiles whose sum is equal to roll
        actions = []
        for r in range(1, len(open_tiles)+1):
            for subset in itertools.combinations(open_tiles, r):
                if sum(subset) == roll:
                    actions.append(subset)
        return actions

    def next_state(self, open_tiles, action):
        #close the tiles in 'action' and return the new state
        new_tiles = [t for t in open_tiles if t not in action]
        return tuple(new_tiles)

    def expected_wins(self, state):
        if state in self.memo:
            return self.memo[state]
        
        open_tiles, roll = state
        
        tile_sum = sum(open_tiles)

        #Terminal States
        if not self.p1_score and tile_sum == 0: #p1 auto win- closes all tiles
            return 1.0
        if self.p1_score and tile_sum < self.p1_score: #p2 better score
            return 1.0
        
        values = []
        for i in range(2, 13) if tile_sum > 6 else range(1, 7): #roll 1 or 2 dice based on tile_sum
            max_win = float('-inf')

            actions = self.get_possible_actions(open_tiles, i)
            if not actions: #Terminal States- no moves
                if not self.p1_score: #p1 terminal states
                    max_win = max(max_win, 1 - self.p2_prob[tile_sum])
                elif self.p1_score: #p2 terminal states
                    if tile_sum == self.p1_score: #ties score
                        max_win = max(max_win, 0.5)
                    elif tile_sum > self.p1_score: #worse score
                        max_win = max(max_win, 0.0)

            for action in actions:
                next_state = (self.next_state(open_tiles, action), i) 
                next_win = self.expected_wins(next_state)
                max_win = max(max_win, next_win)
            if tile_sum <= 6:
                values.append((1/6) * max_win)
            else:
                values.append(self.prob[i] * max_win)
                
        self.memo[state] = sum(values)
        return self.memo[state]

    def optimal_move(self, open_tiles, roll):
        actions = self.get_possible_actions(open_tiles, roll)
        best_action = None
        best_value = float('-inf')

        for action in actions:
            next_state = (self.next_state(open_tiles, action), None)
            value = self.expected_wins(next_state)
            if value > best_value:
                best_value = value
                best_action = action

        return best_action

    def solve(self):
        if self.action == "--expect":
            initial_state = (tuple(map(int, self.position)), self.roll)
            print(f"{self.expected_wins(initial_state):.6f}")
        elif self.action == "--move":
            open_tiles = tuple(map(int, self.position))
            best_action = self.optimal_move(open_tiles, self.roll)
            if best_action:
                print(f"[{', '.join(map(str, sorted(best_action)))}]")
            else:
                print([])


if __name__ == "__main__":

    #Use dp to compute values for p2 but pre-compute the expected_wins for p2 given a target score from p1
    # for i in range(0, 46):
    #     args = sys.argv[1:]
    #     player = "--two"
    #     action = "--expect"
    #     position = "123456789"
    #     p1_score = i
    #     roll = None
    #     game = ShutTheBox(player, action, position, p1_score, roll)
    #     print(i, ": ", end="") 
    #     game.solve()


    args = sys.argv[1:]
    player = args[0]  #--one or --two
    action = args[1]  #--expect or --move
    position = args[2] #tiles that aren't closed
    if player == "--two":
        p1_score = int(args[3])
        roll = int(args[4]) if action == "--move" else None
    else:
        p1_score = None
        roll = int(args[3]) if action == "--move" else None

    game = ShutTheBox(player, action, position, p1_score, roll)
    game.solve()