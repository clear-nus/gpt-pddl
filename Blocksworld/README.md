# README

## Startup

Python version: 3.7.16

Install the requirements. It is recommended to create a virtual environment. The `openai`, `tarski` and `networkx` packages are necessary for the core scripts, while others are mainly used for analysis and visualisation.

```bash
pip install -r requirements.txt
```

In the current directory (where the `setup.py` lies in), install the local package (add `-e` if you want to install in editable mode):

```bash
pip install .
```

Then, set up the environment variable for reference to our working directory:

```bash
cd Language2PDDL
export ROOT_DIR=$(pwd)
```

Set up OpenAI API key environment variable (required only for the n-shot inference):

```bash
export API_KEY=REPLACE_THIS_WITH_YOUR_OPENAI_API_KEY
```

## PDDL Template Generation

Run `Language2PDDL/domains/blocksworld/gen_pddl.sh` to generate PDDL problem templates for benchmark construction. 

## Benchmark Generation

Run `Language2PDDL/domains/blocksworld/gen_pddl.sh` to generate all benchmarks.

Valid choices of `TASK_TYPE`s and their meanings are as follows:

* standard_stack - ExplicitStacks
* stack_seq_b2t - ExplicitStacks-II, described from bottom to top
* stack_seq_t2b - ExplicitStacks-II, described from top to bottom
* stack_seq_t2b_rev - ExplicitStacks-II, described from top to bottom, different predicate order in example
* constr_h1 - NBlocks
* constr_heq - KStacks
* constr_hprime - PrimeStack
* constr_c1 - BlockAmbiguity
* constr_ceq - KStacksColor

This script executes the `gen_data.py` script. The python script accepts an `--dump-ft` option, which tells the script to dump the dataset in a JSONL format that suits the OpenAI finetuning interface. Though we do not include finetuning in our final experiment setup, we still use this format throughout our n-shot inference and evaluation process.

The value of the `--dump-ft` option also controls the type of generated benchmark.

* `goal` - standard PDDL goal translation benchmark
* `list` - benchmark for goal inference
* `check` - benchmark for domain understanding

The main process of dataset generation is executed only when the `--dump-ft` option is not provided. When provided, the script transforms **existing** generated dataset into the JSONL format.

## N-Shot Inference

Run `Language2PDDL/domains/blocksworld/fewshot_test.sh` to run the inference on all tasks. For choices of `TASK_TYPE`, see [Benchmark Generation](#benchmark-generation).

**This is the only script that involves OpenAI API call and requires the API key.**

All responses are stored locally (under `Language2PDDL/results` by default).

## Result Evaluation
 
Run `Language2PDDL/scripts/evaluation.py` to make further analysis on stored responses.

To evaluate all responses under the result folder, run:

```bash
evaluation.py --mode all
```

To get the domain understanding test results for successes, run:

```bash
evaluation.py --mode dom_und --case succ
```

For results on failing cases, run:

```bash
evaluation.py --mode dom_und --case fail
```

To get the report on goal inference for these two cases, replace `dom_und` with `goal_inf`.