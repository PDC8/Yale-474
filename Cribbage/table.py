from cribbage import Game
import scoring

import csv

class Table:
    def __init__(self):
        self.game = Game()
        self.table = [[0 for _ in range(13)] for _ in range(13)]

    def generate_table(self, n, am_dealer):
        for i, rank1 in enumerate(self.game.all_ranks()):
            for j, rank2 in enumerate(self.game.all_ranks()):
                self.table[i][j] = self.compute_vP(n, rank1, rank2, am_dealer)
                print("running")
    
    def compute_vP(self, n, rank1, rank2, am_dealer):
        total_score = 0
        for i in range(n):
            deck = self.game.deck() #new deck
            crib = []
            #shuffle it to randomly remove the first 2 cards with the same rank as the rank pair we chose
            deck.shuffle()
            for c in deck._cards:
                if rank1 == c._rank:
                    crib.append(c)
                    deck.remove([c])
                    break
            for c in deck._cards:
                if rank2 == c._rank:
                    crib.append(c)
                    deck.remove([c])
                    break
            deck.shuffle()
            opp_hand = deck.deal(6) # deal 6 cards for opp's hand 
            deck.shuffle()
            cut_card = deck.deal(1) # deal 1 card for cut card

            keep, throw, score = None, None, None
            if am_dealer: #I am dealer then crib belongs to me and opp doesn't own crib
                keep, throw, score = scoring.greedy_throw(self.game, opp_hand, -1)
            else: #opp is dealer who owns crib
                keep, throw, score = scoring.greedy_throw(self.game, opp_hand, 1)
            crib += throw

            total_score += scoring.score(self.game, crib, cut_card[0], True)[0]
        return round((total_score / n), 2)


    def get_table(self):
        return self.table

if __name__ == "__main__":
    table = Table()
    table.generate_table(100000, False) #True for my_crib, False for opp_crib
    print(table.get_table())
    with open('output1.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(table.get_table())
        print("CSV file created successfully.")
