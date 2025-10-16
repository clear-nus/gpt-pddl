set -ex

CONFIG=${ROOT_DIR}/domains/blocksworld/gen_data_config.yaml
N_OBJS="4 8 12"
DOMAIN=blocksworld-4ops
DOMAIN_PATH=${ROOT_DIR}/domains/blocksworld/generated_domain.pddl
SAVE_DIR=${ROOT_DIR}/data/pddl_dataset


for N_OBJ in ${N_OBJS}
do
  python gen_pddl.py \
    --config ${CONFIG} \
    --domain_path ${DOMAIN_PATH} \
    --save_dir ${SAVE_DIR}/ \
    --version ${DOMAIN}_obj_${N_OBJ} \
    --object ${N_OBJ}
done