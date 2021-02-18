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
- `jqf`: This is the the framework that implements the Zest algorithm used by Bonsai Fuzzing.
- `picireny`: This is the the implementation of HDD used for baseline reduction.
- `picire`: This is the the implementation of character level DD used for baseline reduction.
- `experiment\_scripts`: Contains various scripts used for running experiments.
- `scripts`: Contains various scripts used for generating figures and tables from the paper.
- `pre-baked`: Contains results of the experiments that were run on the authors' machine.
- `fresh-baked`: This will contain the results of the experiments that you run, after following Part Two.

## Part One: Generating figures in paper

This section explains how to analyze the results in `pre-baked`, which is provided with the artifact, to produce Figures 9-12 and Table 2 in the paper. You can follow the same steps with the results of your own `fresh-baked` experiments in part two, as well.

For each figure we have provided a script `./scripts/generate_figure_X.py`. This script:

1) Generates plottable CSVs from raw run data
2) Generates plots from the CSVs

If the plottable CSVs exist, the script skips straight to step 2. To generate the plots for the full evaluation used in the paper, run all of the following commands:

```
cd $BONSAI_DIR
python scripts/generate_figure_9.py ../pre-baked/csvs/ ../pre-baked/figures_and_tables/
python scripts/generate_figure_10.py ../pre-baked/csvs/ ../pre-baked/figures_and_tables/
python scripts/generate_figure_11.py ../pre-baked/csvs/ ../pre-baked/figures_and_tables/
python scripts/generate_figure_12.py ../pre-baked/csvs/ ../pre-baked/figures_and_tables/
python scripts/generate_table_2.py ../pre-baked/csvs/ ../pre-baked/figures_and_tables/
```

These commands take as arguments the `RESULT_DIR`. The above commands create plots in a sub-directory called `figures_and_tables` inside the `pre-baked` results directory.  You can do the same with `fresh-baked` results to see coverage plots for experiments that you can run following instructions in part two.

Once you run the above command, do `ls pre-baked/figures_and_tables` to list the generated PNGs and CSVs for the `pre-baked` results.

## Part Two: Running fresh experiments

The main evaluation of this paper involves experiments on the two targets ChocoPy and Closure.

The experiments can be launched via `experiment_scripts/run_experiments.py`, whose usage is as follows:

```
python experiment_scripts/run_experiments.py --config config/baseline.yaml
python experiment_scripts/run_experiments.py --config config/bonsai.yaml
```

Where `config` is the name of the YAML file specifying the experimental configurations, 

For the experiments in the paper, we ran with the configurations in `bonsai.yaml` and `baseline.yaml`, which takes **200+ CPU-days**. We recommend running a smaller version of the experiments to get approximate results, configurations can be found under `baseline_fresh_baked.yaml` and `bonsai_fresh_baked.yaml`.

```
python experiment_scripts/run_experiments.py --config config/baseline_fresh_baked.yaml
python experiment_scripts/run_experiments.py --config config/bonsai_fresh_baked.yaml
```

The above command will save results in a directory named `fresh-baked`. These results are the final corpuses of each of the techniques on each of the targets.

