import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
import math
from statsmodels.stats.inter_rater import fleiss_kappa
import krippendorff


class BaseMetaSummarizer:
    optimizer = None
    _IS_FIT = False
    _IS_SOLVE = False
    BREAK_IF_CONVERGENCE = None
    LIST_BEST_FITNESS = list()
    FITNESS_FUNCTION = None

    def __init__(self,
                 N_AGENTS,
                 MAX_ITERATIONS,
                 MAX_KONVERGEN,
                 BREAK_IF_CONVERGENCE,
                 FUNCTIONS,
                 ):
        self.optimizer = {
            "name": None,
            "params": {
                'N_AGENTS': N_AGENTS,
                'MAX_ITERATIONS': MAX_ITERATIONS,
                "MAX_KONVERGEN": MAX_KONVERGEN,
                "FUNCTIONS": {
                    **FUNCTIONS,
                    'lowerbound': 0,
                    'upperbound': 1
                },
            }
        }
        self._IS_SOLVE = False
        self._IS_FIT = False
        self.BREAK_IF_CONVERGENCE = BREAK_IF_CONVERGENCE
        self.LIST_BEST_FITNESS = list()  # record best fitness each iterations
        self.FITNESS_FUNCTION = self.__fitness_function_score
        # check apakah masing-masing parameter yang dimasukan sudah sesuai ketentuan
        if self.optimizer['params']['FUNCTIONS']['compression_rate'] < 0.5 or self.optimizer['params']['FUNCTIONS']['compression_rate'] > 1:
            raise ValueError(
                'Compression rate must be in this interval: 0.5 <= comp_rate <= 1')

    def fit(self, dfs_train):
        """Fit the input data

        Args:
            dfs_train (dict): dictionary of dataframe from each title. The dictionary key contains title and the value contain the df of extracted features from each title. Provide the same shape(dimension) of df in each title. In the last of title you must provide the 'extractive_summary' label which contains 1/0 label, where 1 is important summary sentence and 0 is not important summary sentence
        """
        if not isinstance(dfs_train, dict):
            raise TypeError(
                'Provide dfs_train as dictionary, where key is title text and value is extracted features from each title')

        if len(dfs_train) <= 0:
            raise ValueError('Please insert your dfs_train!')

        # check apakah dimensi yang diberikan user sudah sesuai dengan dimensi dfs_train
        N_FEATURES = self.optimizer['params']['FUNCTIONS']['n_features']
        for title, df in dfs_train.items():
            X = df.drop('labels', axis=1)
            if N_FEATURES != X.shape[1]:
                raise ValueError(
                    f'Please format your df {title} in dfs_train in the same N_FEATURES ({N_FEATURES}) size!')

        self.dfs_train = dfs_train
        self.IS_FIT = True

        return self

    def _initialize_agents(self):
        """
        Function for agents initialization based on size of features
        """
        pass

    def __fitness_function_score(self, df_sentences_score_with_label):
        """Menghitung skor kualitas hasil ringkasan dengan metriks tertentu. Metriks yang bisa digunakan:
        - accuracy: Accuracy Score from scikit-learn metrics
        - fleiss: Fleiss Kappa from package statsmodels.stats.inter_rate
        - krippendorff: Kripendorff Alpha from krippendorff package

        Args:
            df_sentences_score_with_label (_type_): dataframe yang berisi susunan indeks kalimat, total skor per kalimat dari fitur-fitur yang digunakan, label ground truth
        """
        def _calculate_accuracy_score(y_true, y_predicted_labels):
            score = accuracy_score(y_true, y_predicted_labels)
            return score

        def _calculate_fleiss_kappa_score(y_true, y_predicted_labels):
            y_true = y_true.astype(int)
            y_predicted_labels = y_predicted_labels.astype(int)
            annotation_data = np.array([
                y_true,
                y_predicted_labels
            ]).T
            # ada berapa banyak anotator
            num_items = len(annotation_data[:, 0])
            num_categories = 2  # label 0 atau 1
            # transforming data into correct format
            transformed_data = np.zeros((num_items, num_categories))
            for i, item_annotation in enumerate(annotation_data):
                for ann in item_annotation:
                    transformed_data[i, ann] += 1

            # calculate fleiss kappa
            score = fleiss_kappa(transformed_data)
            return score

        def _calculate_krippendorff(y_true, y_predicted_labels):
            y_true = y_true.astype(int)
            y_predicted_labels = y_predicted_labels.astype(int)
            annotation_data = np.array([
                y_true,
                y_predicted_labels
            ])
            score = krippendorff.alpha(reliability_data=annotation_data,
                                       level_of_measurement='nominal')
            return score

        metric = self.optimizer['params']['FUNCTIONS']['metric']
        compression_rate = self.optimizer['params']['FUNCTIONS']['compression_rate']
        n_sentences = df_sentences_score_with_label.shape[0]

        # sorting sentences berdasarkan total sentence score dikalikan weights dari agent
        df_sentences_score_with_label.sort_values(
            by='total_sentence_score', ascending=False, inplace=True)

        # extract Top-N sentences as system summary
        number_of_compressed_sentences = (compression_rate*n_sentences)
        top_n_extracted_sentences = int(np.ceil(n_sentences -
                                                number_of_compressed_sentences))
        sentence_indexes_summary = df_sentences_score_with_label.head(
            top_n_extracted_sentences)['sentence_idx'].values

        # extract label 1/0 dari top-N sentences
        y_predicted_labels = []
        for idx in range(n_sentences):
            if idx < number_of_compressed_sentences:
                y_predicted_labels.append(1)
            else:
                y_predicted_labels.append(0)
        y_predicted_labels = np.array(y_predicted_labels)

        # hitung accuracy score atau ROUGE untuk setiap dokumen
        y_true = df_sentences_score_with_label['labels'].values
        fitness_score = 0
        if metric == 'accuracy':
            fitness_score = _calculate_accuracy_score(
                y_true, y_predicted_labels)
        elif metric == 'fleiss':
            fitness_score = _calculate_fleiss_kappa_score(
                y_true, y_predicted_labels)
        elif metric == 'krippendorff':
            fitness_score = _calculate_krippendorff(
                y_true, y_predicted_labels)

        return fitness_score

    def _evaluate_fitness(self, agents):
        """For each agent in agents we calculate the average accuracy/fleiss/krippendorff using all dfs_train

        Args:
            agents (list): list of agents
        """
        pass

    def _adjust_boundaries(self, agents):
        BATAS_BAWAH = self.optimizer['params']['FUNCTIONS']['lowerbound']
        BATAS_ATAS = self.optimizer['params']['FUNCTIONS']['upperbound']
        for idx_agent, agent in enumerate(agents):
            agents[idx_agent]['position'] = np.clip(
                agents[idx_agent]['position'], BATAS_BAWAH, BATAS_ATAS)
        return agents

    def _retrieve_best_agent(self, agents):
        """
        Function untuk retrieve best agent pada iterasi terakhir setelah di solve
        """
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']

        fitness = np.array([
            agent_data['fitness'] for agent_data in agents
        ])
        best_indices_agents = np.argmin(fitness)
        if OBJECTIVE == 'max':
            best_indices_agents = np.argmax(fitness)

        return agents[best_indices_agents]

    def _retrieve_worst_agent(self, agents):
        """
        Function untuk retrieve worst agent pada iterasi terakhir setelah di solve
        """
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']

        fitness = np.array([
            agent_data['fitness'] for agent_data in agents
        ])
        worst_indices_agents = np.argmax(fitness)
        if OBJECTIVE == 'max':
            worst_indices_agents = np.argmin(fitness)

        return agents[worst_indices_agents]

    def _check_convergence(self, gbest_fitness, best_fitness_previous, convergence, idx_iteration):
        MAX_KONVERGEN = self.optimizer['params']['MAX_KONVERGEN']
        is_break = False
        if math.isclose(best_fitness_previous, gbest_fitness, rel_tol=1e-9, abs_tol=1e-9):
            convergence += 1
        else:
            convergence = 0
        print(
            f'Generation {idx_iteration + 1}, Best Fitness: {gbest_fitness}, Konvergen: {convergence}')

        if convergence == MAX_KONVERGEN:
            print(f'Convergence is reached = {MAX_KONVERGEN}')
            is_break = True

        best_fitness_previous = gbest_fitness
        return is_break, best_fitness_previous, convergence
