import os
import subprocess
import argparse

REDUCE_COMMAND = "$BONSAI_DIR/reduce/reduce.sh {} {} {} {} {}"
class_and_method_names = {
    "chocopy": ("chocopy.fuzz.AnalysisTargetRaw", "runAnalysisRaw"),
    "closure": ("closure.fuzz.ClosureTest", "testWithInputStream")
}
grammars = {
    "chocopy": ("Python3.g4", "file_input"),
    "closure": ("ECMAScript.g4", "program")
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus_dir", required=True, type=str, help="Dir with final corpuses")
    args = parser.parse_args()

    for target in os.listdir(args.corpus_dir):
        classname, method = class_and_method_names[target]
        baseline_dir = os.path.join(args.corpus_dir, target, "baseline")
        reduced_char_dir = os.path.join(baseline_dir, "reducedChar")
        reduced_grammar_dir = os.path.join(baseline_dir, "reducedGrammar")
        if not os.path.isdir(reduced_char_dir):
            os.mkdir(reduced_char_dir)
        if not os.path.isdir(reduced_grammar_dir):
            os.mkdir(reduced_grammar_dir)
        baseline_corpus_dir = os.path.join(baseline_dir, "corpuses")
        for exp in os.listdir(baseline_corpus_dir):
            input_dir = os.path.join(baseline_corpus_dir, exp)
            output_char_dir = os.path.join(reduced_char_dir, exp)
            output_grammar_dir = os.path.join(reduced_grammar_dir, exp)
            grammar_file, start = grammars[target]
            char_reduce_command = REDUCE_COMMAND.format(
                classname,
                method,
                input_dir,
                output_char_dir,
                "picire -a char"
            )
            grammar_reduce_command = REDUCE_COMMAND.format(
                classname,
                method,
                input_dir,
                output_grammar_dir,
                "picireny --grammar $BONSAI_DIR/reduce/{} --start {} --build-hidden-tokens".format(
                    grammar_file,
                    start
                )
            )
            process = subprocess.Popen(char_reduce_command, shell=True)
            process.wait()
            os.remove(os.path.join(output_char_dir, ".*.uniq"))
            os.remove(os.path.join(output_char_dir, ".*.rcov"))
            os.remove(os.path.join(output_char_dir, ".*.cov"))
            process = subprocess.Popen(grammar_reduce_command, shell=True)
            process.wait()
            os.remove(os.path.join(output_grammar_dir, ".*.uniq"))
            os.remove(os.path.join(output_grammar_dir, ".*.rcov"))
            os.remove(os.path.join(output_grammar_dir, ".*.cov"))



