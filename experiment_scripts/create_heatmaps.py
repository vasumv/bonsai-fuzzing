import os
import csv
import subprocess
import pickle
import argparse
import numpy as np
from multiprocessing import Process


def generate_out_list(experiment_dir, min_param_list, max_param_list):
    min_ids, min_items, min_depth = min_param_list
    max_ids, max_items, max_depth = max_param_list
    out_list = [[[0 for d in range(max_depth - min_depth + 1)] for num_items in range(max_items - min_items + 1)]
                  for num_ids in range(max_ids - min_items + 1)]
    for ids in range(min_ids, max_ids + 1):
        for items in range(min_items, max_items + 1):
            for depth in range(min_depth, max_depth + 1):
                param_dir = "{}{}{}".format(ids, items, depth)
                with open(os.path.join(experiment_dir, param_dir, "plot_data")) as csv_file:
                    data = []
                    csv_reader = csv.reader(csv_file, delimiter=",")
                    for row in csv_reader:
                        # Total coverage, valid inputs, invalid inputs, valid coverage
                        data.append((row[6], row[-3], row[-2], row[-1]))
                total_cov, valid, invalid, valid_cov = data[-1]
                total_cov, valid_cov = float(total_cov.strip()[:4]), float(valid_cov.strip()[:4])
                valid, invalid = float(valid.strip()), float(invalid.strip())
                total = valid + invalid
                out_list[0][0][0] = [
                    total,
                    valid,
                    invalid,
                    valid / total,
                    valid_cov
                ]
    return out_list

def run_experiments(experiments_dir, num_experiments, min_param_list, max_param_list, results_dir):
    for n in range(num_experiments):
        experiment_dir = os.path.join(experiments_dir, "exp%d" % n)
        out_list = np.array(generate_out_list(experiment_dir, min_param_list, max_param_list))
        file_name = "experiment%d.npy" % n
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)
        np.save(open(os.path.join(results_dir, file_name), "wb"), out_list)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min_param_list", required=True, type=str, help="Min params for generator")
    parser.add_argument("--max_param_list", required=True, type=str, help="Maximum params for generator")
    parser.add_argument("--experiments_dir", required=True, type=str, help="Output directory of experiments")
    parser.add_argument("--results_dir", required=True, type=str, help="Output directory of all output lists")
    parser.add_argument("--num_experiments", required=True, type=int, help="Number of experiments / processes")
    args = parser.parse_args()

    min_params = [int(d) for d in args.min_param_list]
    max_params = [int(d) for d in args.max_param_list]

    run_experiments(args.experiments_dir, args.num_experiments, min_params, max_params, args.results_dir)

