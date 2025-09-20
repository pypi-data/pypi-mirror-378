from metasummarizer.BaseMetaSummarizer import BaseMetaSummarizer
import numpy as np


class BaseMetaSummarizerFeatureSelection (BaseMetaSummarizer):

    def __init__(self,
                 N_AGENTS,
                 MAX_ITERATIONS,
                 MAX_KONVERGEN,
                 BREAK_IF_CONVERGENCE,
                 FUNCTIONS,
                 ):
        super().__init__(
            N_AGENTS=N_AGENTS,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )

    def fit(self, X_train, y_train, X_dev, y_dev):
        """
        Function untuk memasukkan data training X_train,y_train dan data testing X_dev, y_dev dalam bentuk array untuk proses optimasi (feature selection).

        <INPUT>
        - X_train: n-d array format as input variables
        - y: n-d array format as label (dependent variables)
        """
        self.X_train = X_train
        self.y_train = y_train
        self.X_dev = X_dev
        self.y_dev = y_dev
        self.N_FEATURES = X_train.shape[1]

    def solve(self):
        pass

    def _initialize_agents(self):
        """
        Function untuk initialize random agents sebagai solusi awal. Setiap agent memiliki dimensi N dengan N menyatakan jumlah fitur dari dataset yang dimasukkan. Setiap elemen pada setiap dimensi merupakan nilai biner 1/0 yang menyatakan aktif atau tidaknya suatu fitur

        <Output>
        - agents: n-d dimensional array in numpy format containing 1/0 bit
        """

        agents = np.random.randint(
            2, size=(self.optimizer['params']['N_AGENTS'], self.N_FEATURES))
        return agents
