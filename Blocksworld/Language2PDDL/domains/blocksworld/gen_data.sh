set -ex

CONFIG=${ROOT_DIR}/domains/blocksworld/gen_data_config.yaml
DOMAIN=blocksworld-4ops
DOMAIN_PATH=${ROOT_DIR}/domains/blocksworld/generated_domain.pddl
SAVE_DIR=${ROOT_DIR}/data/pddl_dataset/dataset/blocksworld_objects

for TASK_TYPE in standard_stack stack_seq_b2t stack_seq_t2b stack_seq_t2b_rev constr_h1 constr_heq constr_hprime constr_c1 constr_ceq
 do
  python gen_data.py \
    --config ${CONFIG} \
    --domain_path ${DOMAIN_PATH} \
    --save_dir ${SAVE_DIR} \
    --task_type ${TASK_TYPE} 

  python gen_data.py \
    --config ${CONFIG} \
    --domain_path ${DOMAIN_PATH} \
    --save_dir ${SAVE_DIR} \
    --task_type ${TASK_TYPE} \
    --dump_ft goal

  python gen_data.py \
    --config ${CONFIG} \
    --domain_path ${DOMAIN_PATH} \
    --save_dir ${SAVE_DIR} \
    --task_type ${TASK_TYPE} \
    --dump_ft list

  python gen_data.py \
    --config ${CONFIG} \
    --domain_path ${DOMAIN_PATH} \
    --save_dir ${SAVE_DIR} \
    --task_type ${TASK_TYPE} \
    --dump_ft check
done