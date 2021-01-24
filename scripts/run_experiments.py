import os
import subprocess
import argparse
import yaml
from multiprocessing import Process
from collections import defaultdict
from shutil import copy2

MVN_FUZZ_COMMAND = """
mvn jqf:fuzz -Dclass={} -Dmethod={} -Dtarget={} -Dout={} -Dtime={}\
    -DmaxIdentifiers={} -DmaxItems={} -DmaxDepth={}\
    -Dexcludes=kotlin,venus -Djqf.ei.DISABLE_SAVE_NEW_COUNTS=true\
"""

MVN_REPRO_ARGS_COMMAND= """
mvn jqf:repro -Dclass={} -Dmethod={} -Dinput={} -DdumpArgsDir={}\
    -DmaxIdentifiers={} -DmaxItems={} -DmaxDepth={}
"""

def add_parent(parent, graph, bound, visited, depth, depth_map):
    if tuple(parent) in visited:
        return
    for i in range(len(parent)):
        child = parent[:]
        if child[i] == bound:
            continue
        if i == 3 and child[i] == 1:
            continue
        child[i] += 1
        graph[tuple(child)].append(parent)
        add_parent(child, graph, bound, visited, depth + 1, depth_map)
    depth_map[depth].append(parent)
    visited.add(tuple(parent))

def create_graph(bound):
    graph = defaultdict(list)
    depth_map = defaultdict(list)
    visited = set()
    root = [1, 1, 1, 0]
    add_parent(root, graph, bound, visited, 0, depth_map)
    return graph, depth_map

def join_seed_dirs(target_dir, seed_dirs):
    seed_dir_names = [''.join([str(p) for p in d]) for d in seed_dirs]
    new_seed_dir = '_'.join(seed_dir_names) + "_seed"
    full_new_seed_dir = os.path.join(target_dir, new_seed_dir)
    if not os.path.exists(full_new_seed_dir):
        os.mkdir(full_new_seed_dir)
    files = []
    for seed_dir in seed_dir_names:
        full_seed_dir = os.path.join(target_dir, seed_dir + "/corpus/")
        filenames = os.listdir(full_seed_dir)
        files += [os.path.join(full_seed_dir, f) for f in filenames]
    files.sort(key=lambda f: os.stat(f).st_size)
    counter = 0
    for f in files:
        new_file_name = 'id_' + str(counter).zfill(6)
        copy2(f, os.path.join(full_new_seed_dir, new_file_name))
        counter += 1
    return full_new_seed_dir


def run_experiment(class_name, method_name, param_list, runtime, target_dir, seed_dirs, technique, experiment_num):
    target_dir = os.path.join(target_dir, "exp%d" % experiment_num)
    experiment_dir = "".join([str(d) for d in param_list])
    command = MVN_FUZZ_COMMAND.format(class_name, method_name, target_dir, experiment_dir, runtime, *param_list[:3])
    if technique == "bonsai":
        assert len(param_list) == 4
        if (param_list[3] == 0):
            command += " -Djqf.ei.SAVE_ONLY_VALID=true"
        if len(seed_dirs) > 0:
            full_seed_dir = join_seed_dirs(target_dir, seed_dirs)
            command += " -Din={}".format(full_seed_dir)
    print(command)
    process = subprocess.Popen(command, shell=True)
    process.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=str, help="YAML File for experiment config")
    args = parser.parse_args()

    with open(args.config, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    assert (config["target"] == "chocopy" or config["target"] == "closure"), \
                "Target must be one of 'chocopy', 'closure'"
    assert (config["technique"] == "baseline" or config["technique"] == "bonsai"), \
                "Target must be one of 'baseline', 'bonsai'"

    class_name, method_name = "", ""
    if config["target"] == "chocopy":
        class_name, method_name = "chocopy.fuzz.AnalysisTargetValid", "runAnalysisValid"
    elif config["target"] == "closure":
        class_name, method_name = "closure.fuzz.ClosureTest", "testWithIterativeGenerator"

    graph, depth_map = create_graph(config["max_bound"])
    params = [config["max_bound"]] * 3

    for i in range(config["num_experiments"]):
        if config["technique"] == "bonsai":
            for d in range(len(depth_map)):
                params = depth_map[d]
                print(params)
                procs = []
                for param_list in params:
                    p = Process(target=run_experiment, args=(class_name,
                                                            method_name,
                                                            param_list,
                                                            config["runtime"],
                                                            config["target_dir"],
                                                            graph[tuple(param_list)],
                                                            config["technique"],
                                                            i))
                    p.start()
                    procs.append(p)
                for p in procs:
                    p.join()
        else:
            run_experiment(class_name, method_name, params,
                           config["runtime"], config["target_dir"], [], config["technique"], i)

    max_level = max(depth_map)
    final_params = (
        depth_map[max_level][0] if config["technique"] == "bonsai"
        else params
    )
    final_param_dir = "".join(str(p) for p in final_params)
    for i in range(config["num_experiments"]):
        exp_dir = "exp%d" % i
        final_corpus_dir = os.path.join(config["target_dir"], exp_dir, final_param_dir, "corpus")
        dest_corpus_dir = os.path.join(config["results_dir"], config["target"], config["technique"], "corpuses", exp_dir)
        repro_command = MVN_REPRO_ARGS_COMMAND.format(class_name, method_name, final_corpus_dir,
                                          dest_corpus_dir, *final_params[:3])
        print(repro_command)
        process = subprocess.Popen(repro_command, shell=True)
        process.wait()



