from src.simcalibration.dg_models.DGModel import DGModel
import pandas as pd
from dagsim.base import Graph
from simcalibration.utils.Data import Data
import numpy as np
import os
# Define results folder path
figuredirname = os.sep + "results" + os.sep
results_path = os.path.join(os.getcwd(), "results")

# Make sure folder exists
os.makedirs(results_path, exist_ok=True)

# Full path for the CSV file
csv_full_path = os.path.join(results_path, "dataOutput.csv")

class DagsimModel(DGModel):
    def __init__(self, name, dagsim_model: Graph):
        super().__init__(name=name, SLClass=None, learned=True)
        self.model = dagsim_model
        # Default variable order: all observed nodes (incl. outcome) in the graph’s topological order
        observed = [n for n in self.model.adj_mat.columns
                    if self.model.get_node_by_name(n).observed]
        self.var_names = observed  # can be overridden later to match data order

    def instantiate(self):
        pass

    def fit(self, data: pd.DataFrame, **kwargs):
        pass

    @property
    def dag(self) -> np.ndarray:
        """
        Return true adjacency (observed variables only) in current self.var_names order.
        """
        if self.var_names is None:
            # fallback to observed nodes in adj_mat order
            self.var_names = [n for n in self.model.adj_mat.columns
                              if self.model.get_node_by_name(n).observed]
        A = self.model.adj_mat.loc[self.var_names, self.var_names]
        return A.astype(int).to_numpy()

    def set_var_order(self, var_names):
        """Optionally force a canonical variable order for downstream comparisons."""
        self.var_names = list(var_names)

    def _generate(self, num_samples: int, outcome_name: str):
        data = pd.DataFrame.from_dict(self.model.simulate(num_samples, csv_name=csv_full_path))
        data = data.fillna(0).replace({1.0: 1, 0.0: 0})
        return Data(name=self.name, X=data.drop(columns=[outcome_name]), y=data.loc[:, outcome_name])
