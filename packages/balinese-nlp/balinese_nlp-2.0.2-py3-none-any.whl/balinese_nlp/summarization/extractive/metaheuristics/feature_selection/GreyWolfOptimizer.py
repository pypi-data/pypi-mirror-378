from metasummarizer.feature_selection.BaseMetaSummarizerFeatureSelection import BaseMetaSummarizerFeatureSelection


class GreyWolfOptimizer(BaseMetaSummarizerFeatureSelection):
    def __init__(self,
                 N_WOLVES=50,
                 MAX_ITERATIONS=100,
                 MAX_KONVERGEN=10,
                 OPTIMIZER_NAME='Grey Wolf Optimizer',
                 FUNCTIONS={
                     'n_features': 2,
                     'compression_rate': 0.67,  # must be 0.5 <= comp_rate <= 1
                     'objective': 'max',
                     # metrics for evaluating each agent fitness {accuracy, fleiss, krippendorff}
                     'metric': 'accuracy'
                 },
                 BREAK_IF_CONVERGENCE=True
                 ):
        """Grey Wolf Optimizer for optimizing weight features in Balinese Extractive Text Summarization

        Args:
            N_WOLVES (int): number of grey wolf individuals. Defaults to 50.
            MAX_ITERATIONS (int): maximum iterations. Defaults to 100.
            MAX_KONVERGEN (int): optimization will be stoped after MAX_KONVERGEN iterations. Defaults to 4.
            OPTIMIZER_NAME (str): your optimizer name will be. Defaults to 'Grey Wolf Optimizer'.
            FUNCTIONS (dict): objective function criteria. Defaults to { 'n_features': 4, 'compression_rate': 0.57,  # must be 0.5 <= comp_rate <= 1 'objective': 'max', 'metric': 'accuracy' # {accuracy, fleiss, kripendorff_alpha} }.
            BREAK_IF_CONVERGENCE (bool): flag if optimization will be stopped after MAX_KONVERGEN. Defaults to True.
        """
        super().__init__(
            N_AGENTS=N_WOLVES,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )
        self.optimizer['name'] = OPTIMIZER_NAME

    def _initialize_agents(self):
        """
        Initialize solution in binary format 1/0 for feature selection problem

        """
        super()._initialize_agents()
