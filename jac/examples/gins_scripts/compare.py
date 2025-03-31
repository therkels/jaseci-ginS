import os
from natsort import natsorted
import pickle
from jaclang.runtimelib.gins.cfg import CFG
from jaclang.runtimelib.gins.model import Gemini
from jaclang.compiler.semtable import SemRegistry
import random
import json
import numpy as np

def compare_hot_paths(cfg_object: CFG, cfg_dict: str):
    """
    Compare the hot paths (sequence of nodes) between a CFG object and a Cfg JSON string.

    Args:
        cfg_object (CFG): An instance of the CFG class.
        cfg_json_str (str): A JSON string representation of the CFG.

    Returns:
        None
    """
    # Parse the JSON string into a dictionary
    # cfg_dict = json.loads(cfg_json_str)

    # Extract hot path from CFG object
    def extract_hot_path(cfg_obj: CFG):
        visited = set()
        path = []

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            if node in cfg_obj.edges:
                for succ in cfg_obj.edges[node]:
                    dfs(succ)

        for node in cfg_obj.nodes:
            if node not in visited:
                dfs(node)
        return path

    object_hot_path = extract_hot_path(cfg_object)

    # Extract hot path from JSON dictionary
    def extract_json_hot_path(cfg_dict) :
        visited = set()
        path = []
        edges = {bb['bb_id']: [edge['edge_to_bb_id'] for edge in bb['edges']] for bb in cfg_dict['cfg_bbs']}

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            if node in edges:
                for succ in edges[node]:
                    dfs(succ)

        for bb in cfg_dict['cfg_bbs']:
            node = bb['bb_id']
            if node not in visited:
                dfs(node)
        return path

    json_hot_path = extract_json_hot_path(cfg_dict)

    # Compare the paths
    if object_hot_path == json_hot_path:
        print("The hot paths are identical.")
        return True
    else:
        print("The hot paths differ.")
        print(f"CFG Object Hot Path: {object_hot_path}")
        print(f"JSON Hot Path: {json_hot_path}")
        return False


file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'predictions_no_context.pkl')

no_of_edges = None

import pandas as pd

eval_data = pd.DataFrame(columns=['Hot Path Predicted', 'Error Rate', 'Error Avg', 'Error Std'])

with open(file_path, 'rb') as file:
    cfg_data=(pickle.load(file))
for i,data in enumerate(cfg_data):
    path_predicted_correctly = False
    error_rate = 0
    error_avg = 0
    error_std = 0
    print(f"\nSample :{i}\n")
    inputs = data['input']
    actula_cfg = data['cfgs']
    predicted_cfg = data['Predicted']
    # print(inputs)
    # print(actula_cfg)
    # print(predicted_cfg)

    predicted_cfg = json.loads(predicted_cfg)

    # Extract edges from the CFG object
    object_edge_frequencies = actula_cfg.edge_counts

    # Extract edges from the dictionary
    dict_edge_frequencies = {}
    for bb in predicted_cfg['cfg_bbs']:
        for edge in bb['edges']:
            from_bb = bb['bb_id']
            to_bb = edge['edge_to_bb_id']
            frequency = edge['freq']
            dict_edge_frequencies[(from_bb, to_bb)] = frequency

    # Compare frequencies
    if no_of_edges is None:
        no_of_edges = len(object_edge_frequencies)
    for edge, obj_freq in object_edge_frequencies.items():
        dict_freq = dict_edge_frequencies.get(edge, None)
        if dict_freq is None:
            print(f"Edge {edge} is in CFG object but missing in the dictionary.")
        elif obj_freq != dict_freq:
            print(f"Mismatch for edge {edge}: Object freq = {obj_freq}, Dict freq = {dict_freq}.")
            error_rate += 1
            diff = abs(obj_freq - dict_freq)
            error_avg += diff
    error_avg /= no_of_edges
    error_rate /= no_of_edges
    error_std = np.std([abs(object_edge_frequencies[edge] - dict_edge_frequencies.get(edge, 0)) for edge in object_edge_frequencies])

 
    for edge, dict_freq in dict_edge_frequencies.items():
        if edge not in object_edge_frequencies:
            print(f"Edge {edge} is in the dictionary but missing in the CFG object.")

    # Compare hot paths
    path_predicted_correctly = compare_hot_paths(actula_cfg, predicted_cfg)

    eval_data.loc[i] = [path_predicted_correctly, error_rate, error_avg, error_std]


print(eval_data)
# Write the evaluation data to a CSV file
output_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evaluation_no_ctx_results.csv')
eval_data.to_csv(output_csv_path, index=False)
print(f"Evaluation results saved to {output_csv_path}")