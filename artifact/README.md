# Bonsai Fuzzing: Artifact

This document has the following sections:
- **Setup**: Make sure that the provided Docker container runs on your system.
- **Part one: Generating figures in the paper**: Analyze pre-baked results of the full experiments, which were generated on the authors' machine in roughly 0.6 compute-years. Run scripts to produce the figures used in the paper. You can also use these instructions on the results from part two to produce figures for your own fresh-baked experiments, which should approximate the figures in the paper (though that will take a bit longer).
- **Part two: Running fresh experiments** (~10 human-minutes + ~2 compute-hours): Run the experiments to a fresh-baked set of the evaluation results.

## Getting-started

### Requirements

* You will need **Docker** on your system. You can get Docker CE for Ubuntu here: https://docs.docker.com/install/linux/docker-ce/ubuntu. See links on the sidebar for installation on other platforms.

You will need about 4GB of free disk space + memory to run the container and experiments.

### Load image

To load the artifact on your system, pull the image from the public repo.
```
docker pull vasumv/bonsai-fuzzing-artifact
```

### Run container

Run the following to start a container and get a shell in your terminal:

```
docker run --name bonsai-fuzzing -it vasumv/bonsai-fuzzing-artifact
```

The remaining sections of this document assume that you are inside the container's shell, within the default directory `/bonsai-fuzzing. 

### Container filesystem

The default directory in the container, `/home/bonsai-fuzzing-artifact`, contains the following contents:
- `README.txt`: This file.
- `bonsai-fuzzing`: This is the Bonsai Fuzzing implementation.
- `bonsai-fuzzing/pre-baked`: Contains results of the experiments that were run on the authors' machine.
- `bonsai-fuzzing/experiment_scripts`: Contains various scripts used for running experiments.
- `bonsai-fuzzing/scripts`: Contains various scripts used for generating figures and tables from the paper.
- `bonsai-fuzzing/fresh-baked`: This will contain the results of the experiments that you run, after following Part Two.
- `jqf`: This is the the framework that implements the Zest algorithm used by Bonsai Fuzzing.
- `picireny`: This is the the implementation of HDD used for baseline reduction.
- `picire`: This is the the implementation of character level DD used for baseline reduction.

### Setting Environment Variables
First, run a script to set the proper environment variables used for running experiments:
```
. /home/bonsai-fuzzing-artifact/bonsai-fuzzing/scripts/set_env_vars.sh
```

## Part One: Generating figures in paper

This section explains how to analyze the results in `pre-baked`, which is provided with the artifact, to produce Figures 9-12 and Table 2 in the paper. You can follow the same steps with the results of your own `fresh-baked` experiments in part two, as well.

There is a script `./script/generate_csv.py` that will generate plottable CSVs from the raw data in the corpuses. These plottable CSVs
have already been generated for the pre-baked data and can be found under `pre-baked/csvs/`. Part 2 elaborates on 
running this script for `fresh-baked` results.

For each figure we have provided a script `./scripts/generate_figure_X.py`. This script generates plots from plottable CSVs.

To generate the plots for the full evaluation used in the paper, run all of the following commands:

```
cd $BONSAI_DIR
python3 scripts/generate_figure_9.py pre-baked/heatmaps/ pre-baked/figures_and_tables/
python3 scripts/generate_figure_10.py --csv_file pre-baked/csvs/corpus_results.csv --fig_dir pre-baked/figures_and_tables/
python3 scripts/generate_figure_11.py --csv_file pre-baked/csvs/validity_results.csv --fig_dir pre-baked/figures_and_tables/
python3 scripts/generate_figure_12.py --csv_file pre-baked/csvs/coverage_results.csv --fig_dir pre-baked/figures_and_tables/
python3 scripts/generate_table_2.py --csv_file pre-baked/csvs/num_files_results.csv --fig_dir pre-baked/figures_and_tables/
```

These commands take as arguments `csv_file` and `fig_dir` (with the exception of figure 9, which takes in the heatmap raw results directory). You can `fresh-baked` results to see coverage plots for experiments that you can run following instructions in part two.

Once you run the above command, do `ls fig_dir` to list the generated PNGs and CSVs for the `pre-baked` results.

## Part Two: Running fresh experiments

The main evaluation of this paper involves experiments on the two targets ChocoPy and Closure. 
The experiments can be launched via `experiment_scripts/run_experiments.py`, whose usage is as follows:

```
python3 experiment_scripts/run_experiments.py --target chocopy \
                                   --technique bonsai \
                                   --experiments 10 \
                                   --time 60m \
                                   --output-dir fresh-baked/finalCorpuses
```
where `target` is either `chocopy` or `closure`, `technique` is either `bonsai` or `baseline`, `experiments` is the number of repetitions,
`time` is the time for each fuzzing session, and `output_dir` is the directory where results will be saved.

For the experiments in the paper, we used `experiments`=`10, time`=`60m` for Bonsai and `time`=`3240m` for baseline (equivalent fuzzing time). We ran on both targets.

Additionally, we ran DD and HDD to reduce the baseline corpuses, which can be done as follows:
```
python3 experiment_scripts/reduce_baseline.py --corpus_dir fresh-baked/finalCorpuses
```
The  `corpus_dir` argument corresponds to the `output_dir` from running `run_experiments.py`. The script will create two new 
directories `reducedChar` and `reducedGrammar` for each baseline corpus.

Overall, the experiments with these configurations take ~**200+ CPU-days**. We recommend running a smaller version of the experiments to get approximate results, e.g:
```
python3 experiment_scripts/run_experiments.py --target chocopy \
                                   --technique bonsai \
                                   --experiments 1 \
                                   --time 1m \
                                   --output-dir fresh-baked/finalCorpuses

```
The above command will save results in a directory named `fresh-baked`. You can run corresponding commands for 
the baseline and the other targets. Afterwards, to generate the CSV files for plotting figures and creating tables,
run the following commands:

```
python3 scripts/generate_csv.py --corpus_dir fresh-baked/finalCorpuses --output_dir fresh-baked/csvs/ --metric validity
python3 scripts/generate_csv.py --corpus_dir fresh-baked/finalCorpuses --output_dir fresh-baked/csvs/ --metric coverage
python3 scripts/generate_csv.py --corpus_dir fresh-baked/finalCorpuses --output_dir fresh-baked/csvs/ --metric corpus
python3 scripts/generate_csv.py --corpus_dir fresh-baked/finalCorpuses --output_dir fresh-baked/csvs/ --metric num_files
```

