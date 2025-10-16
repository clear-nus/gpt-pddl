set -ex

for TASK_TYPE in standard_stack stack_seq_b2t stack_seq_t2b stack_seq_t2b_rev constr_h1 constr_heq constr_hprime constr_c1 constr_ceq
do
  for MODE in goal list check
  do
    python fewshot_test.py \
      --config ${ROOT_DIR}/domains/blocksworld/gen_data_config.yaml \
      --task_type $TASK_TYPE \
      --mode $MODE \
      --api_key $API_KEY
  done
done