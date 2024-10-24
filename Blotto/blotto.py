import sys
import numpy as np
from scipy.optimize import linprog
import itertools
from collections import defaultdict

def generate_combinations(total_units, num_battlefields):
    combinations = []
    for counts in itertools.product(range(total_units + 1), repeat=num_battlefields):
        if sum(counts) == total_units:
            combinations.append(list(counts))

    return combinations


def calculate_payoff(strategy_p1, strategy_p2, fieldValues, objective):
    total_points_p1 = 0
    total_points_p2 = 0

    for i in range(len(fieldValues)):
        p1_units = strategy_p1[i]
        p2_units = strategy_p2[i]
        if objective == '--score' or objective == '--win':
            if p1_units > p2_units:
                total_points_p1 += fieldValues[i]
            elif p1_units < p2_units:
                total_points_p2 += fieldValues[i]
            else:
                total_points_p1 += fieldValues[i] / 2
                total_points_p2 += fieldValues[i] / 2
        elif objective == '--lottery':
            if p1_units > p2_units:
                total_points_p1 += fieldValues[i] * (p1_units ** 2 / (p1_units ** 2 + p2_units ** 2))
                total_points_p2 += fieldValues[i] * (p2_units ** 2 / (p1_units ** 2 + p2_units ** 2))
            elif p1_units < p2_units:
                total_points_p1 += fieldValues[i] * (p1_units ** 2 / (p1_units ** 2 + p2_units ** 2))
                total_points_p2 += fieldValues[i] * (p2_units ** 2 / (p1_units ** 2 + p2_units ** 2))
            else:
                total_points_p1 += fieldValues[i] / 2
                total_points_p2 += fieldValues[i] / 2
    if objective == '--win':
        if total_points_p1 > total_points_p2:
            return 1
        elif total_points_p2 > total_points_p1:
            return 0
        else:
            return 0.5
        
    return total_points_p1


def generate_payoff_matrix(unit_combinations, fieldValues, objective):
    num_strategies = len(unit_combinations)
    payoff_matrix = np.zeros((num_strategies, num_strategies))

    for i, strat_p1 in enumerate(unit_combinations):
        for j, strat_p2 in enumerate(unit_combinations):
            payoff_matrix[i, j] = calculate_payoff(strat_p1, strat_p2, fieldValues, objective)

    return payoff_matrix


def find_equilibrium(units, fieldValues, objective, tolerance):
    # Generate all possible combinations of unit distributions
    unit_combinations = generate_combinations(units, len(fieldValues))
    
    # Generate the payoff matrix based on the objective
    payoff_matrix = generate_payoff_matrix(unit_combinations, fieldValues, objective)
    
    num_strategies = len(unit_combinations)

    # Objective function: Minimize -v == Maximize v
    c = [0] * num_strategies + [-1]

    #A_ub @ x <= b_ub
    A_ub = []
    b_ub = []

    for col in range(num_strategies):
        row = [-payoff_matrix[i, col] for i in range(num_strategies)] + [1]  # Coefficients for x_i and v
        A_ub.append(row)
        b_ub.append(0)

    #x1 + x2 + x3 + 0v <= 1
    A_ub.append([1] * num_strategies + [0])
    b_ub.append(1)
    #-x1 -x2 -x3 + 0v <= -1
    A_ub.append([-1] * num_strategies + [0])
    b_ub.append(-1)

    # #A_eq @ x = b_eq
    # A_eq = [[1] * num_strategies + [0]]  # This represents x1 + x2 + ... + x3 = 1
    # b_eq = [1]
    
    # 0 <= xi <= 1
    bounds = [(0, 1)] * num_strategies + [(None, None)]  
     
    # Solve the linear programming problem
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    if res.success:
        probabilities = res.x[:-1]
        
        # Output the strategy if probabilities exceed the tolerance
        for i, prob in enumerate(probabilities):
            if prob > tolerance:
               strategy_str = ",".join(map(str, unit_combinations[i]))
               print(f"{strategy_str},{prob:.17f}")


def verify_equilibrium(fieldValues, objective, tolerance):
    dict_values = defaultdict(float)
    units = None

    # Read strategy from standard input
    for line in sys.stdin:
        parts = line.strip().split(',')
        strategy = tuple(map(int, parts[:-1]))
        if units == None:
            units = sum(strategy)
        prob =  float(parts[-1])
        dict_values[strategy] = prob

    #check to make sure is a valid equilibrium 
    if not np.isclose(sum(dict_values.values()), 1.0, atol=tolerance):
        print("Failed: Probabilities do not sum to 1 within tolerance")
        return
    

    unit_combinations = generate_combinations(units, len(fieldValues))

    E_XY = 0.0
    E_IY_list = []
    E_XI_list = [0] * len(unit_combinations)
    for strat1 in unit_combinations:
        prob_strat1 = dict_values[tuple(strat1)]
        E_IY = 0.0
        for j, strat2 in enumerate(unit_combinations):
            prob_strat2 = dict_values[tuple(strat2)]
            payoff = calculate_payoff(strat1, strat2, fieldValues, objective)
            E_XY += prob_strat1 * prob_strat2 * payoff
            E_IY += prob_strat2 * payoff
            E_XI_list[j] += prob_strat1 * payoff
        E_IY_list.append(E_IY)
    
    #check to see if E(i, Y) <= E_XY <= E(X, j) for all i,j. If not it terminates and doesn't pass
    for i in range(len(unit_combinations)):
        if E_IY_list[i] > E_XY + tolerance or E_XI_list[i] < E_XY - tolerance:
            print(f"E[X, {unit_combinations[i]}] = {E_XI_list[i]} < {E_XY} < E[{unit_combinations[i]}, Y] = {E_IY_list[i]}")
            return
    print("PASSED")


def main():
    args = sys.argv[1:]
    action = args[0]
    tolerance = 1e-6
    objective = None
    i = 0
    units = None
    fieldValues = []


    if args[1] == "--tolerance":
        tolerance = float(args[2])
        objective = args[3]
        i = 4
    else:
        objective = args[1]
        i = 2

    if action == "--find" and args[i] == "--units":
        units = int(args[i + 1])
        i += 2
    fieldValues = [int(arg) for arg in args[i:]]

    if action == "--find":
        find_equilibrium(units, fieldValues, objective, tolerance)
        
    elif action == "--verify":
        verify_equilibrium(fieldValues, objective, tolerance)

    return 0


if __name__ == "__main__":
    main()