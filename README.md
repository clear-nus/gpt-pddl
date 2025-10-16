# Translating natural language to planning goals with large-language models


Official implementation for the paper: [Translating Natural Language to Planning Goals with Large-Language Models](https://arxiv.org/pdf/2302.05128)

This is an official implementation for 
A comprehensive benchmark and framework for evaluating language models' ability to translate natural language instructions into formal PDDL (Planning Domain Definition Language) goal specifications across multiple domains.

## Overview

This repository contains implementations and benchmarks for testing language models on three key capabilities:

1. **Goal Translation**: Converting natural language instructions to PDDL goal states
2. **Domain Understanding**: Comprehending planning domain semantics and constraints
3. **Goal Inference**: Reasoning about implicit requirements and task completion criteria

The framework spans two distinct domains with varying complexity levels:

- **Blocksworld**: Classic planning domain with explicit and implicit stack configurations
- **Alfred**: Household robotics tasks with partial specifications and open-ended objectives

## Repository Structure

```
.
├── Blocksworld/                          # Blocksworld domain tasks
│   ├── domains/blocksworld/              # PDDL templates and generation scripts
│   ├── scripts/                          # Evaluation utilities
│   └── README.md                         # Detailed Blocksworld documentation
│
├── Alfred/
│   ├── Alfred_Partially-Specified-Tasks_1to8/    # Tasks with incomplete specifications
│   │   ├── generate_initial_states.py            # Initial state generation
│   │   ├── generate_goal_pddl.py                 # Goal state generation
│   │   ├── evaluate.py                           # Task-specific evaluation
│   │   └── README.md                             # Partially-specified tasks guide
│   │
│   └── Alfred_Open-Ended-Tasks_9to13/            # Complex household tasks
│       ├── openai_gen.py                         # NL to PDDL translation
│       ├── domain/                               # PDDL domain definitions
│       └── README.md                             # Open-ended tasks guide
│
└── README.md                             # This file
```

## Quick Start

### Prerequisites

- Python 3.7.16 or higher
- OpenAI API key (for n-shot inference)


## Task Domains

### Blocksworld

The Blocksworld domain includes nine task types testing different aspects of goal specification:

- **ExplicitStacks**: Direct stack configurations
- **ExplicitStacks-II**: Sequential descriptions (top-to-bottom, bottom-to-top)
- **NBlocks**: Constraints on block counts
- **KStacks**: Constraints on stack counts
- **PrimeStack**: Stack height prime number constraints
- **BlockAmbiguity**: Ambiguous block references
- **KStacksColor**: Color-based stack constraints

See [Blocksworld/README.md](Blocksworld/README.md) for detailed setup and evaluation instructions.

### Alfred Household Tasks

#### Partially-Specified Tasks (Tasks 1-8)

Seven task types focusing on spatial reasoning and quantitative constraints:

- **MoveSynonym**: Synonym understanding in movement commands
- **MoveNextTo**: Relative positioning
- **MoveToCount2/3**: Multi-object counting constraints
- **MoveToMore**: Comparative quantity reasoning
- **MoveNested/Nested2**: Hierarchical spatial relationships

See [Alfred/Alfred_Partially-Specified-Tasks_1to8/README.md](Alfred/Alfred_Partially-Specified-Tasks_1to8/README.md) for generation and evaluation procedures.

#### Open-Ended Tasks (Tasks 9-13)

Five realistic household scenarios:

- **CutFruits**: Slice and plate fruits
- **PrepareMeal**: Arrange meal components
- **IceCream**: Organize refrigerator contents
- **SetTable2**: Configure dining setup
- **CleanKitchen**: Organize kitchen items

See [Alfred/Alfred_Open-Ended-Tasks_9to13/README.md](Alfred/Alfred_Open-Ended-Tasks_9to13/README.md) for task descriptions and usage.

## Workflow

### 1. Benchmark Generation

Generate PDDL problem templates and initial states for your chosen domain:

**Blocksworld:**
```bash
cd Blocksworld
bash domains/blocksworld/gen_pddl.sh
```

**Alfred (Partially-Specified):**
```bash
cd Alfred/Alfred_Partially-Specified-Tasks_1to8
python generate_initial_states.py --init_path init_states --scene scene9
```

### 2. Goal State Generation

Translate natural language instructions to PDDL goals:

**Blocksworld:**
```bash
bash domains/blocksworld/fewshot_test.sh
```

**Alfred (Partially-Specified):**
```bash
python generate_goal_pddl.py --scene scene9 --init_path init_states --gen_path gen_results
```

**Alfred (Open-Ended):**
```bash
python openai_gen.py
```

### 3. Evaluation

Evaluate generated goal states and model capabilities:

**Blocksworld:**
```bash
python scripts/evaluation.py --mode all
```

**Alfred (Partially-Specified):**
```bash
python evaluate.py --scene scene9 --init_path init_states --gen_path gen_results
```
**Alfred (Partially-Specified):**

Human Evaluated


### Evaluation Metrics

The framework evaluates three dimensions:

1. **Goal Translation Success**: Correctness of generated PDDL goal specifications
2. **Domain Understanding**: Accuracy on domain-specific comprehension questions
3. **Goal Inference**: Ability to infer implicit task requirements

Results include both success rates and detailed error analysis for each capability.

### Configuration Options

#### Zero-shot vs One-shot

Toggle between zero-shot and one-shot learning by adding the `--zero_shot` flag:

```bash
python generate_goal_pddl.py --scene scene9 --init_path init_states --gen_path gen_results --zero_shot
```

#### Partial Evaluation

Evaluate only a subset of test cases:

```bash
python evaluate.py --scene scene9 --init_path init_states --gen_path gen_results --num_case 50
```

## Citation

If you use this benchmark in your research, please cite:

```bibtex
@article{xie2023translating,
  title={Translating natural language to planning goals with large-language models},
  author={Xie, Yaqi and Yu, Chen and Zhu, Tongyao and Bai, Jinbin and Gong, Ze and Soh, Harold},
  journal={arXiv preprint arXiv:2302.05128},
  year={2023}
}
```