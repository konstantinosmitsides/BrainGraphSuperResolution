from MatrixVectorizer import MatrixVectorizer

from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr
from scipy.spatial.distance import jensenshannon
import torch
import networkx as nx
import numpy as np
from tqdm import tqdm

# # the following numbers do not reflect the provided dataset, just for an example
# num_test_samples = 20
# num_roi = 10

# # create a random model output 
# pred_matrices = torch.randn(num_test_samples, num_roi, num_roi).numpy()

# # post-processing
# pred_matrices[pred_matrices < 0] = 0

# # create random ground-truth data
# gt_matrices = torch.randn(num_test_samples, num_roi, num_roi).numpy()

# # you do NOT need to that since the ground-truth data we provided you is alread pre-processed.
# gt_matrices[gt_matrices < 0] = 0

def evaluate_predictions(tensor_pred, tensor_true):

    """ 
    tensor_pred and tensor_true should both be tensors of shape
    (num_val_samples, hr_dim, hr_dim).

    """

    # Initialize lists to store MAEs for each centrality measure
    mae_bc = []
    mae_ec = []
    mae_pc = []

    pred_1d_list = []
    gt_1d_list = []

    # Iterate over each test sample
    for i in tqdm(range(len(tensor_pred)), desc='Evaluating Predictions (Can be Slow)'):

        pred_matrix = tensor_pred[i].cpu().detach().numpy()
        true_matrix = tensor_true[i].cpu().detach().numpy()

        # Convert adjacency matrices to NetworkX graphs
        pred_graph = nx.from_numpy_array(pred_matrix, edge_attr="weight")
        gt_graph = nx.from_numpy_array(true_matrix, edge_attr="weight")

        # Compute centrality measures
        pred_bc = nx.betweenness_centrality(pred_graph, weight="weight")
        pred_ec = nx.eigenvector_centrality(pred_graph, weight="weight")
        pred_pc = nx.pagerank(pred_graph, weight="weight")

        gt_bc = nx.betweenness_centrality(gt_graph, weight="weight")
        gt_ec = nx.eigenvector_centrality(gt_graph, weight="weight")
        gt_pc = nx.pagerank(gt_graph, weight="weight")

        # Convert centrality dictionaries to lists
        pred_bc_values = list(pred_bc.values())
        pred_ec_values = list(pred_ec.values())
        pred_pc_values = list(pred_pc.values())

        gt_bc_values = list(gt_bc.values())
        gt_ec_values = list(gt_ec.values())
        gt_pc_values = list(gt_pc.values())

        # Compute MAEs
        mae_bc.append(mean_absolute_error(pred_bc_values, gt_bc_values))
        mae_ec.append(mean_absolute_error(pred_ec_values, gt_ec_values))
        mae_pc.append(mean_absolute_error(pred_pc_values, gt_pc_values))

        # Vectorize matrices
        pred_1d_list.append(MatrixVectorizer.vectorize(pred_matrix))
        gt_1d_list.append(MatrixVectorizer.vectorize(true_matrix))

    # Compute average MAEs
    avg_mae_bc = sum(mae_bc) / len(mae_bc)
    avg_mae_ec = sum(mae_ec) / len(mae_ec)
    avg_mae_pc = sum(mae_pc) / len(mae_pc)

    # Concatenate flattened matrices
    pred_1d = np.concatenate(pred_1d_list)
    gt_1d = np.concatenate(gt_1d_list)

    # Compute metrics
    mae = mean_absolute_error(pred_1d, gt_1d)
    pcc = pearsonr(pred_1d, gt_1d)[0]
    js_dis = jensenshannon(pred_1d, gt_1d)

    print("MAE: ", mae)
    print("PCC: ", pcc)
    print("Jensen-Shannon Distance: ", js_dis)
    print("Average MAE betweenness centrality:", avg_mae_bc)
    print("Average MAE eigenvector centrality:", avg_mae_ec)
    print("Average MAE PageRank centrality:", avg_mae_pc)
    
    all_metrics = {
        'mae': mae,
        'pcc': pcc,
        'js_dis': js_dis,
        'avg_mae_bc': avg_mae_bc,
        'avg_mae_ec': avg_mae_ec,
        'avg_mae_pc': avg_mae_pc,
    }
    
    return all_metrics