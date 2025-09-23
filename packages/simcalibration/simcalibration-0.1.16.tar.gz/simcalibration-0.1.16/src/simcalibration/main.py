from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
import argparse
import warnings
import time
from sklearn.tree import DecisionTreeClassifier
from simcalibration.dg_models.Bnlearner import Bnlearner
from simcalibration.ml_models.SklearnModel import SklearnModel
from simcalibration.utils.Evaluator import Evaluator
from simcalibration.utils.Andes_Dag import get_andes
from simcalibration.utils.Postprocressing import Postprocessing
from sklearn.metrics import balanced_accuracy_score
import random
import numpy as np
import os
from simcalibration.utils.Win95_Dag import get_printer

figuredirname = os.path.join(os.getcwd(), "results")
os.makedirs(figuredirname, exist_ok=True)

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
warnings.simplefilter(action='ignore', category=FutureWarning)

def run_metasimulation(
    n_train=200,
    n_test=200,
    n_true_repetitions=10,
    n_practitioner_repetitions=10,
    n_sl_repetitions=5,
    kfolds=2
):
    starttime = time.time()
    ########################################################################################################################
    # To run a meta-simulation in SimCal, the user needs to specify three elements
    #
    # 1) Configure the ground truth DAG of the real-world, specifying the structure and parameters of the Bayesian Network
    # 2) Configure the Machine Learning Estimators used for benchmarking and their hyper-parameters
    # 3) Configure the Structural Learners used to learn the underlying distribution (i.e., estimate DAGs) from limited data
    ########################################################################################################################

    # =========================
    # Bayesian Network
    # =========================
    ds_model = get_printer()  # WIN95PTS
    # ds_model = get_andes()  # ANDES
    # ds_model = get_asia()   # ASIA

    ########################################################################################################################
    # Machine Learning configuration, select and specialise the algorithm using a custom network or import an existing network (www.bnlearn.com/bnrepository/)
    # For example:
    # list_sklearn = []
    # list_sklearn.append(SklearnModel("SVCSigmoid", svm.SVC, kernel="sigmoid"))
    # list_sklearn.append(SklearnModel("GradientBoostingClassifier_logloss", GradientBoostingClassifier, loss="log_loss"))
    # list_sklearn.append(SklearnModel("RandomForestClassifier_entropy", RandomForestClassifier, criterion="entropy"))
    # list_sklearn.append(SklearnModel("LogisticLASSO", LogisticRegression, penalty="l1", solver="liblinear"))
    ########################################################################################################################
    list_sklearn = [
        SklearnModel("AdaBoostClassifier", AdaBoostClassifier, random_state=SEED),
        SklearnModel("RandomForestClassifier", RandomForestClassifier, random_state=SEED),
        SklearnModel("MLPClassifier", MLPClassifier, solver='lbfgs', max_iter=5000, hidden_layer_sizes=(10, 2), random_state=SEED),
        SklearnModel("DecisionTreeClassifier_gini", DecisionTreeClassifier, criterion="gini", random_state=SEED),
        SklearnModel("DecisionTreeClassifier_entropy", DecisionTreeClassifier, criterion="entropy", random_state=SEED)
    ]
    ########################################################################################################################
    # Structural Learner configuration, define and configure the learning algorithms used to estimate DAGs from limited data
    # For example:
    # structural_learner_list = []
    # structural_learner_list.append(Bnlearner(name="hc", SLClass="hc"))
    # structural_learner_list.append(Bnlearner(name="iamb", SLClass="iamb"))
    # structural_learner_list.append(NotearsLearner(name="notears_linear", SLClass="notears_linear", loss_type='logistic', lambda1=0.01))
    ########################################################################################################################
    structural_learner_list = [
        Bnlearner(name="hc", SLClass="hc"),
        Bnlearner(name="tabu", SLClass="tabu"),
        Bnlearner(name="rsmax2", SLClass="rsmax2"),
        Bnlearner(name="mmhc", SLClass="mmhc"),
        Bnlearner(name="h2pc", SLClass="h2pc"),
        Bnlearner(name="gs", SLClass="gs"),
        Bnlearner(name="pc.stable", SLClass="pc.stable")
    ]
    # =========================
    # Evaluator
    # =========================
    evaluator = Evaluator(
        ml_models=list_sklearn,
        dg_models=structural_learner_list,
        real_models=[ds_model],
        scores=[balanced_accuracy_score],
        outcome_name="Y"
    )
    # =========================
    # Meta-simulation
    # =========================
    metasimulation_benchmarks = evaluator.meta_simulate(
        ds_model,
        n_learning=0,
        n_train=n_train,
        n_test=n_test,
        n_true_repetitions=n_true_repetitions,
        n_practitioner_repetitions=n_practitioner_repetitions,
        n_sl_repetitions=n_sl_repetitions,
        kfolds=kfolds
    )
    pp = Postprocessing()
    pp.meta_simulation_visualise(metasimulation_benchmarks)
    endtime = time.time()
    print("Time taken: ", endtime - starttime)

# =========================
# CLI interface
# =========================
def main():
    parser = argparse.ArgumentParser(description="Run SimCalibration meta-simulation")
    parser.add_argument("--n_train", type=int, default=200)
    parser.add_argument("--n_test", type=int, default=200)
    parser.add_argument("--n_true_repetitions", type=int, default=10)
    parser.add_argument("--n_practitioner_repetitions", type=int, default=10)
    parser.add_argument("--n_sl_repetitions", type=int, default=5)
    parser.add_argument("--kfolds", type=int, default=2)

    args = parser.parse_args()
    run_metasimulation(
        n_train=args.n_train,
        n_test=args.n_test,
        n_true_repetitions=args.n_true_repetitions,
        n_practitioner_repetitions=args.n_practitioner_repetitions,
        n_sl_repetitions=args.n_sl_repetitions,
        kfolds=args.kfolds
    )


if __name__ == "__main__":
    main()