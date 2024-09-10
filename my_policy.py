from policy import CribbagePolicy, CompositePolicy, GreedyThrower, GreedyPegger
import itertools
import scoring
import random
from collections import defaultdict

class MyPolicy(CribbagePolicy):
    def __init__(self, game):
        self._policy = CompositePolicy(game, GreedyThrower(game), GreedyPegger(game))
        #see table.py for how these were generated
        self._my_crib =[
            [5.53, 4.6, 4.75, 5.39, 5.52, 4.04, 4.06, 4.06, 3.7, 3.71, 3.97, 3.65, 3.56],
            [4.6, 6.03, 7.1, 4.94, 5.61, 4.24, 4.26, 4.11, 4.08, 3.93, 4.17, 3.88, 3.79],
            [4.77, 7.1, 6.26, 5.36, 6.26, 4.11, 4.16, 4.33, 4.06, 3.99, 4.23, 3.94, 3.83],
            [5.39, 4.94, 5.34, 6.02, 6.69, 4.29, 4.13, 4.27, 4.01, 3.84, 4.11, 3.81, 3.72],
            [5.52, 5.6, 6.27, 6.7, 8.76, 6.77, 6.17, 5.59, 5.44, 6.66, 6.96, 6.62, 6.5],
            [4.07, 4.25, 4.12, 4.28, 6.75, 6.05, 5.23, 4.91, 5.31, 3.38, 3.62, 3.29, 3.21],
            [4.07, 4.25, 4.16, 4.11, 6.19, 5.22, 6.21, 6.81, 4.25, 3.41, 3.7, 3.39, 3.3],
            [4.09, 4.1, 4.32, 4.27, 5.59, 4.89, 6.8, 5.71, 4.85, 3.99, 3.66, 3.41, 3.31],
            [3.7, 4.07, 4.07, 4.03, 5.44, 5.31, 4.23, 4.84, 5.3, 4.46, 4.05, 3.15, 3.12],
            [3.7, 3.93, 3.97, 3.86, 6.68, 3.36, 3.4, 4.0, 4.43, 4.99, 4.56, 3.64, 2.95],
            [3.95, 4.18, 4.21, 4.13, 6.93, 3.59, 3.7, 3.66, 4.06, 4.58, 5.49, 4.63, 3.9],
            [3.64, 3.86, 3.91, 3.81, 6.63, 3.29, 3.38, 3.4, 3.15, 3.66, 4.61, 4.86, 3.55],
            [3.56, 3.78, 3.85, 3.71, 6.5, 3.21, 3.31, 3.32, 3.12, 2.96, 3.9, 3.56, 4.65]
        ]

        self._opp_crib = [
            [5.78, 4.77, 4.91, 5.66, 5.95, 4.65, 4.5, 4.55, 4.31, 4.13, 4.35, 4.05, 3.98],
            [4.76, 6.14, 7.18, 5.13, 5.98, 4.73, 4.7, 4.5, 4.53, 4.26, 4.49, 4.18, 4.11],
            [4.92, 7.17, 6.49, 5.66, 6.57, 4.62, 4.62, 4.69, 4.49, 4.35, 4.59, 4.28, 4.2],
            [5.65, 5.11, 5.66, 6.26, 7.11, 4.96, 4.5, 4.6, 4.53, 4.2, 4.46, 4.17, 4.07],
            [5.95, 5.97, 6.56, 7.1, 9.17, 7.31, 6.75, 6.06, 6.04, 7.15, 7.43, 7.1, 7.0],
            [4.66, 4.75, 4.62, 4.96, 7.28, 6.76, 6.07, 5.6, 6.0, 4.06, 4.25, 3.95, 3.87],
            [4.51, 4.7, 4.62, 4.48, 6.72, 6.09, 6.69, 7.43, 5.01, 3.97, 4.27, 3.96, 3.88],
            [4.55, 4.48, 4.68, 4.59, 6.06, 5.58, 7.39, 6.2, 5.58, 4.63, 4.2, 3.94, 3.85],
            [4.33, 4.53, 4.5, 4.52, 6.03, 6.0, 5.01, 5.57, 6.08, 5.15, 4.75, 3.84, 3.82],
            [4.13, 4.25, 4.35, 4.22, 7.16, 4.03, 3.97, 4.63, 5.16, 5.58, 5.21, 4.2, 3.53],
            [4.36, 4.49, 4.59, 4.46, 7.4, 4.27, 4.27, 4.22, 4.73, 5.22, 6.04, 5.18, 4.46],
            [4.04, 4.18, 4.29, 4.15, 7.11, 3.94, 3.94, 3.93, 3.83, 4.21, 5.17, 5.36, 4.12],
            [3.97, 4.09, 4.23, 4.08, 7.0, 3.87, 3.88, 3.88, 3.81, 3.52, 4.46, 4.11, 5.2]
        ]


    
        
    def keep(self, hand, scores, am_dealer):
        arg_max = float('-inf')
        throws = []


        for p1, p2 in itertools.combinations(hand, 2):
            remaining_hand = [card for card in hand if not (card == p1 or card == p2)]

            h_crib = self._my_crib[p1.rank() - 1][p2.rank() - 1] if am_dealer else self._opp_crib[p1.rank() - 1][p2.rank() - 1]
            h_hand = scoring.score(self._policy._game, remaining_hand, None, False)[0]

            if am_dealer:
                if h_hand + h_crib == arg_max:
                    throws.append([p1, p2])
                elif h_hand + h_crib > arg_max:
                    throws = [[p1, p2]]
                    arg_max = h_hand + h_crib
            else:
                if h_hand - h_crib == arg_max:
                    throws.append([p1, p2])
                elif h_hand - h_crib > arg_max:
                    throws = [[p1, p2]]
                    arg_max = h_hand - h_crib

        rand_idx = 0
        if len(throws) > 1:
            rand_idx = random.randint(0, len(throws) - 1)

        throw = throws[rand_idx]
        keep = [card for card in hand if not (card == throw[0] or card == throw[1])]

        # return self._policy.keep(hand, scores, am_dealer)
        return keep, throw


