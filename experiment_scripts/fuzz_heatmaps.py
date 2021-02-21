import os
import csv
import subprocess
import argparse
import numpy as np

MVN_COMMAND = "mvn jqf:fuzz -Dclass={} -Dmethod={} -Dtarget=tmp/heatmaps/ -Dout={} -Dtime={} -DmaxIdentifiers={} -DmaxItems={} -DmaxDepth={} -Dexcludes=kotlin,venus -Djqf.ei.DISABLE_SAVE_NEW_COUNTS=true -Dblind=true"

def run_experiment(class_name, method_name, param_list, runtime, out_list):
    experiment_dir = "{}{}{}".format(*param_list)
    command = MVN_COMMAND.format(class_name, method_name, experiment_dir, runtime, *param_list)
    print(command)
    process = subprocess.Popen(command, shell=True)
    process.wait()
    data = []
    with open(os.path.join("tmp/heatmaps/", experiment_dir, "plot_data")) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            # Total coverage, valid inputs, invalid inputs, valid coverage
            data.append((row[6], row[-3], row[-2], row[-1]))
    total_cov, valid, invalid, valid_cov = data[-1]
    total_cov, valid_cov = float(total_cov.strip()[:4]), float(valid_cov.strip()[:4])
    valid, invalid = float(valid.strip()), float(invalid.strip())
    total = valid + invalid
    max_ids, max_items, max_depth = param_list
    out_list[max_ids - 1][max_items - 1][max_depth - 1] = [
        total,
        valid / total,
        total_cov,
        valid_cov
    ]

def run_experiments(experiment_num, class_name, method_name, min_param_list, max_param_list, runtime, results_dir, out_list):
    min_ids, min_items, min_depth = min_param_list
    max_ids, max_items, max_depth = max_param_list
    for ids in range(min_ids, max_ids + 1):
        for items in range(min_items, max_items + 1):
            for depth in range(min_depth, max_depth + 1):
                run_experiment(class_name, method_name, [ids, items, depth],
                                  runtime, out_list)
    file_name = "experiment%d.npy" % experiment_num
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
    np.save(os.path.join(results_dir, file_name), out_list)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_param_list", required=True, type=str, help="Maximum params for generator")
    parser.add_argument("--runtime", required=True, type=str, help="Time of JQF fuzzing in minutes for each experiment")
    parser.add_argument("--results_dir", required=True, type=str, help="Output directory of heatmaps raw data")
    parser.add_argument("--num_experiments", required=True, type=int, help="Number of experiments")
    args = parser.parse_args()
    class_name, method_name = "chocopy.fuzz.AnalysisTargetValid", "runAnalysisValid"

    if not os.path.isdir(args.results_dir):
        os.mkdir(args.results_dir)

    min_params = [1, 1, 1]
    max_params = [int(d) for d in args.max_param_list]
    out_list = [[[0 for d in range(max_params[2])] for num_items in range(max_params[1])]
                  for num_ids in range(max_params[0])]
    for i in range(args.num_experiments):
        run_experiments(i, class_name, method_name, min_params, max_params, args.runtime, args.results_dir, out_list)
