import numpy as np
import itertools  # <-- THIS WAS MISSING
from scipy.optimize import linear_sum_assignment
from deap import algorithms, base, creator, tools
import random

class SmartScheduler:
    def __init__(self):
        self.setup_genetic_algorithm()
    
    def setup_genetic_algorithm(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

    def optimize(self, events, time_slots, preferences):
        """Automatically selects best scheduling algorithm"""
        num_events = len(events)
        num_slots = len(time_slots)
        
        if num_events <= 5:
            return self.branch_and_bound(events, time_slots, preferences)
        elif num_events == num_slots:
            return self.hungarian_algorithm(events, time_slots, preferences)
        else:
            return self.genetic_algorithm(events, time_slots, preferences)

    def branch_and_bound(self, events, time_slots, preferences):
        """Optimal for small problems (≤5 events)"""
        best_schedule, best_score = None, float('inf')
        for perm in itertools.permutations(range(len(time_slots))):
            score = sum(preferences[i, perm[i]] for i in range(len(events)))
            if score < best_score:
                best_score, best_schedule = score, perm
        return [time_slots[i] for i in best_schedule], best_score

    def hungarian_algorithm(self, events, time_slots, preferences):
        """Optimal for equal numbers of events and slots"""
        row_ind, col_ind = linear_sum_assignment(preferences)
        return [time_slots[i] for i in col_ind], preferences[row_ind, col_ind].sum()

    def genetic_algorithm(self, events, time_slots, preferences):
        """Best for complex/large schedules"""
        toolbox = base.Toolbox()
        toolbox.register("permutation", random.sample, range(len(time_slots)), len(time_slots))
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.permutation)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("mate", tools.cxPartialyMatched)
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("evaluate", lambda ind: sum(preferences[i, ind[i]] for i in range(len(events))))

        pop = toolbox.population(n=200)
        algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=100)
        
        best = tools.selBest(pop, k=1)[0]
        return [time_slots[i] for i in best], toolbox.evaluate(best)[0]