set -ex

DOMAIN_PATH=${ROOT_DIR}/domains/blocksworld/generated_domain.pddl
PROBLEM_PATH=${ROOT_DIR}/results/completion/pddl_files/blocksworld/finetuned_davinci/instance-107.pddl
PLAN_PATH=${ROOT_DIR}/domains/blocksworld/example_plan.txt

python simulator.py \
  --domain_path $DOMAIN_PATH \
  --problem_path $PROBLEM_PATH \
  --plan_path $PLAN_PATH