from .BaseMetaSummarizerWeights import BaseMetaSummarizerWeights
import random as rd
import numpy as np
import math


class SlimeMouldAlgorithm(BaseMetaSummarizerWeights):
    def __init__(self,
                 N_SLIMES=15,
                 MAX_ITERATIONS=100,
                 MAX_KONVERGEN=10,
                 Z_VALUE=0.67,
                 OPTIMIZER_NAME='Slime Mould Algorithm',
                 FUNCTIONS={
                     'n_features': 2,
                     'compression_rate': 0.67,  # must be 0.5 <= comp_rate <= 1
                     'objective': 'max',
                     # metrics for evaluating each agent fitness {accuracy, fleiss, krippendorff}
                     'metric': 'accuracy'
                 },
                 BREAK_IF_CONVERGENCE=True
                 ):
        super().__init__(
            N_AGENTS=N_SLIMES,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )
        self.optimizer['name'] = OPTIMIZER_NAME
        self.optimizer['params'].update({
            'Z_VALUE': Z_VALUE
        })

    def solve(self):
        """
        Menjalankan proses optimasi Slime Mould Algorithm (SMA).
        """
        if not self.IS_FIT:
            raise ValueError(
                'Please fit your data first through fit() method!')

        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        N_SLIMES = self.optimizer['params']['N_AGENTS']

        # 1. Initialize agents
        agents = self._initialize_agents()

        # 2. Evaluate fitness and select the best and worst agents
        agents = self._evaluate_fitness(agents)
        best_agent = self._retrieve_best_agent(agents)
        worst_agent = self._retrieve_worst_agent(agents)
        best_fitness_previous = best_agent['fitness']
        self.LIST_BEST_FITNESS.append(best_agent['fitness'])

        # 3. Optimization process
        convergence = 0
        for idx_iteration in range(MAX_ITERATIONS):
            # Sort slime moulds based on their fitness values
            isDescendingOrder = True
            OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']
            if OBJECTIVE == 'min':
                isDescendingOrder = False

            # Create a list of tuples (agent, fitness) for sorting
            slime_moulds_with_fitness = [
                (agent, agent['fitness']) for agent in agents]
            slime_moulds_with_fitness.sort(
                key=lambda x: x[1], reverse=isDescendingOrder)
            sorted_agents = [agent for agent, _ in slime_moulds_with_fitness]

            # Calculate the weights vector for each agent
            weights_vector = self.__calculate_weights_vector(
                sorted_agents, best_agent, worst_agent)

            # Update slime mould positions
            agents = self.__update_slime_position(
                agents, weights_vector, best_agent, worst_agent, idx_iteration)

            # adjust boundaries
            # agents = self._adjust_boundaries(agents)

            # Evaluate fitness of the new positions
            agents = self._evaluate_fitness(agents)

            # Retrieve new best and worst agents
            best_agent = self._retrieve_best_agent(agents)
            worst_agent = self._retrieve_worst_agent(agents)

            # Check for convergence
            self.LIST_BEST_FITNESS.append(best_agent['fitness'])
            is_break, best_fitness_previous, convergence = self._check_convergence(
                best_agent['fitness'], best_fitness_previous, convergence, idx_iteration)

            if is_break and self.BREAK_IF_CONVERGENCE:
                break

        self._IS_SOLVE = True
        return best_agent

    def __calculate_weights_vector(self, sorted_agents, best_agent, worst_agent):
        """
        Menghitung vector bobot untuk setiap agen berdasarkan paper asli SMA.
        """
        weights_vector = []
        best_fitness = best_agent['fitness']
        worst_fitness = worst_agent['fitness']

        # Handle division by zero
        if best_fitness == worst_fitness:
            return np.ones(len(sorted_agents))

        # Calculate weights based on formula
        for idx_agent, agent in enumerate(sorted_agents):
            fitness_score = agent['fitness']

            # Handle logarithm input constraint
            log_input = (best_fitness - fitness_score) / \
                (best_fitness - worst_fitness) + 1
            if log_input <= 0:
                w = 0.0  # Or a small positive number
            else:
                w = np.log10(log_input)

            # Apply W_i formula (Eq. 3)
            # This logic is based on the fitness ranking (i.e., the sorted order)
            if idx_agent < math.ceil(len(sorted_agents) / 2):
                w = 1 + np.random.rand() * w
            else:
                w = 1 - np.random.rand() * w

            weights_vector.append(w)

        return np.array(weights_vector)

    def __update_slime_position(self, agents, weights_vector, best_agent, worst_agent, iteration):
        """
        Memperbarui posisi setiap agen berdasarkan formula pergerakan SMA.
        """
        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        N_DIMENSION = self.optimizer['params']['FUNCTIONS']['n_features']
        LOWER_BOUND = self.optimizer['params']['FUNCTIONS']['lowerbound']
        UPPER_BOUND = self.optimizer['params']['FUNCTIONS']['upperbound']
        Z_VALUE = self.optimizer['params']['Z_VALUE']
        slime_best_position = best_agent['position']

        # Calculate p, vb, and vc
        p = np.tanh(abs(best_agent['fitness'] - worst_agent['fitness']))

        # --- PERBAIKAN PENTING UNTUK MENGHINDARI OVERFLOW ---
        # Memastikan argumen np.arctanh selalu dalam rentang yang valid (-1, 1).
        arg_a = 1 - (iteration / MAX_ITERATIONS)
        if arg_a >= 1:
            arg_a = 1 - np.finfo(float).eps  # Cap at 1-epsilon
        elif arg_a <= -1:
            arg_a = -1 + np.finfo(float).eps  # Cap at -1+epsilon
        a = 2 * np.arctanh(arg_a)

        # Update positions
        for idx_agent, agent in enumerate(agents):
            if np.random.rand() < Z_VALUE:
                # Pergerakan acak jika melebihi nilai Z_VALUE
                agents[idx_agent]['position'] = np.random.rand(
                    N_DIMENSION) * (UPPER_BOUND - LOWER_BOUND) + LOWER_BOUND
            else:
                if np.random.rand() < p:
                    # Pergerakan menuju best_agent dengan osilasi (Eq. 2.1)
                    vb = np.random.uniform(-a, a, N_DIMENSION)
                    agents[idx_agent]['position'] = slime_best_position + \
                        vb * (weights_vector[idx_agent] * agent['position'])
                else:
                    # Pergerakan acak atau eksplorasi acak (Eq. 2.2)
                    vc = np.random.uniform(-a, a, N_DIMENSION)
                    agents[idx_agent]['position'] = vc * agent['position']

            # Apply boundaries to ensure positions are within the search space
            # agents[idx_agent]['position'] = np.clip(
            #     agents[idx_agent]['position'], LOWER_BOUND, UPPER_BOUND)

        return agents
